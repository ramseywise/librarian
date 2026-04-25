from typing import Any, Dict, Optional, Type

from pydantic import BaseModel


def compact_contract_from_pydantic(
    model: Type[BaseModel],
    *,
    include_descriptions: bool = True,
    indent: int = 2,
) -> str:
    root_schema: Dict[str, Any] = model.model_json_schema()
    defs: Dict[str, Any] = root_schema.get("$defs", {})

    def _ref_name(ref: str) -> Optional[str]:
        prefix = "#/$defs/"
        return ref[len(prefix) :] if ref.startswith(prefix) else None

    def _merge_dicts(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        out = dict(a)
        out.update(b)
        return out

    def _resolve(node: Any) -> Any:
        if not isinstance(node, dict):
            return node

        if "allOf" in node and isinstance(node["allOf"], list) and node["allOf"]:
            merged: Dict[str, Any] = {}
            for part in node["allOf"]:
                part_resolved = _resolve(part)
                if isinstance(part_resolved, dict):
                    merged = _merge_dicts(merged, part_resolved)
            siblings = {k: v for k, v in node.items() if k != "allOf"}
            return _merge_dicts(merged, siblings)

        if "$ref" in node:
            name = _ref_name(node["$ref"])
            target = defs.get(name, {}) if name else {}
            target_resolved = _resolve(target)
            siblings = {k: v for k, v in node.items() if k != "$ref"}
            if isinstance(target_resolved, dict):
                return _merge_dicts(target_resolved, siblings)
            return target_resolved

        return node

    def _fixed_value_comment(s: Dict[str, Any]) -> str:
        """
        Detect a fixed value (Literal[...] / const) and return a short directive comment.
        JSON Schema 'const' means the value must be exactly that constant.  [oai_citation:2‡JSON Schema](https://json-schema.org/understanding-json-schema/reference/generic?utm_source=chatgpt.com)
        """
        s = _resolve(s)

        if "const" in s:
            return f"FIXED: must be {s['const']!r}"

        enum = s.get("enum")
        if isinstance(enum, list) and len(enum) == 1:
            return f"FIXED: must be {enum[0]!r}"

        return ""

    def _type_label(s: Dict[str, Any]) -> str:
        s = _resolve(s)

        if "anyOf" in s and isinstance(s["anyOf"], list):
            parts = [_type_label(p) for p in s["anyOf"]]
            seen, uniq = set(), []
            for p in parts:
                if p not in seen:
                    uniq.append(p)
                    seen.add(p)
            return " | ".join(uniq)

        if "enum" in s and isinstance(s["enum"], list):
            # If it's a single-value enum, we still *show* it as that value set.
            return "|".join(str(x) for x in s["enum"])

        t = s.get("type")
        if t in {"string", "number", "integer", "boolean", "null"}:
            return t
        if t == "array":
            return "array"
        if t == "object" or "properties" in s:
            return "object"
        return "any"

    def _desc(s: Dict[str, Any]) -> str:
        if not include_descriptions:
            return ""
        s = _resolve(s)
        d = s.get("description")
        return str(d).strip() if isinstance(d, str) and d.strip() else ""

    def _render(schema: Dict[str, Any], level: int) -> list[str]:
        schema = _resolve(schema)
        pad = " " * (indent * level)

        # object
        if schema.get("type") == "object" or "properties" in schema:
            props: Dict[str, Any] = schema.get("properties", {}) or {}
            required = set(schema.get("required", []) or [])
            lines = [f"{pad}{{"]
            for k, v in props.items():
                v = _resolve(v)
                key_pad = " " * (indent * (level + 1))

                opt = "" if k in required else " (optional)"
                d = _desc(v)
                fixed = _fixed_value_comment(v)

                # Compose one comment string with priority: FIXED first
                comment_parts = []
                if fixed:
                    comment_parts.append(fixed)
                if d:
                    comment_parts.append(d)
                if opt.strip():
                    comment_parts.append(opt.strip())
                comment = ("  // " + " · ".join(comment_parts)) if comment_parts else ""

                # nested object / array
                if v.get("type") == "array":
                    lines.append(f'{key_pad}"{k}": [')
                    item = (
                        v.get("items", {}) if isinstance(v.get("items"), dict) else {}
                    )
                    lines.extend(_render(item, level + 2))
                    lines.append(f"{key_pad}]{comment}")
                elif v.get("type") == "object" or "properties" in v:
                    lines.append(f'{key_pad}"{k}": ')
                    nested = _render(v, level + 1)
                    nested[0] = nested[0].lstrip()
                    lines[-1] = lines[-1] + nested[0]
                    lines.extend(nested[1:])
                    if comment:
                        lines[-1] = lines[-1] + comment
                else:
                    lines.append(
                        f'{key_pad}"{k}": {_type_label(v)},{comment}'.rstrip(",")
                    )

            lines.append(f"{pad}}}")
            return lines

        # array
        if schema.get("type") == "array":
            lines = [f"{pad}["]
            item = (
                schema.get("items", {}) if isinstance(schema.get("items"), dict) else {}
            )
            lines.extend(_render(item, level + 1))
            lines.append(f"{pad}]")
            return lines

        # primitive fallback
        fixed = _fixed_value_comment(schema)
        d = _desc(schema)
        comment = (
            ("  // " + " · ".join([p for p in [fixed, d] if p])) if (fixed or d) else ""
        )
        return [f"{pad}{_type_label(schema)}{comment}"]

    return "\n".join(_render(root_schema, 0))
