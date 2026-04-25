// ---------------------------------------------------------------------------
// A2UI v0.9 → v0.8 translation adapter
//
// @a2ui/react 0.8.0's processMessages only understands v0.8 message format
// (surfaceUpdate / dataModelUpdate / beginRendering / deleteSurface).
// The agent now emits v0.9 format (createSurface / updateComponents /
// updateDataModel with plain JSON values), so we translate before handing
// off to the library.
// ---------------------------------------------------------------------------

export type V09Component = { id: string; component: string; [key: string]: unknown };
export type V09Message = {
  version?: string;
  createSurface?: { surfaceId: string; catalogId: string; theme?: object };
  updateComponents?: { surfaceId: string; components: V09Component[] };
  updateDataModel?: { surfaceId: string; path?: string; value?: unknown };
  deleteSurface?: { surfaceId: string };
};
export type V08Contents = {
  key: string;
  valueString?: string;
  valueNumber?: number;
  valueBoolean?: boolean;
};

/** Recursively flatten a JSON value to v0.8 typed key-value pairs. */
export function flattenToV08Contents(value: unknown, prefix: string): V08Contents[] {
  if (value === null || value === undefined) return [];
  if (typeof value === "string") return [{ key: prefix, valueString: value }];
  if (typeof value === "number") return [{ key: prefix, valueNumber: value }];
  if (typeof value === "boolean") return [{ key: prefix, valueBoolean: value }];
  if (Array.isArray(value)) {
    // Also store the full array as a JSON string at the prefix key so that
    // path-bound `options` on ChoicePicker can retrieve the whole array via getValue.
    const serialized: V08Contents[] = prefix
      ? [{ key: prefix, valueString: JSON.stringify(value) }]
      : [];
    return [
      ...serialized,
      ...value.flatMap((item, i) =>
        flattenToV08Contents(item, prefix ? `${prefix}.${i}` : String(i))
      ),
    ];
  }
  if (typeof value === "object") {
    return Object.entries(value as Record<string, unknown>).flatMap(([k, v]) =>
      flattenToV08Contents(v, prefix ? `${prefix}.${k}` : k)
    );
  }
  return [];
}

/**
 * Translate a v0.9 children value to v0.8 format:
 *   plain array  → { explicitList: [...] }
 *   template obj { componentId, path } → { template: { componentId, dataBinding } }
 */
function translateChildren(children: unknown): unknown {
  if (Array.isArray(children)) {
    return { explicitList: children };
  }
  if (
    children &&
    typeof children === "object" &&
    "componentId" in (children as object)
  ) {
    const t = children as { componentId: string; path?: string };
    return { template: { componentId: t.componentId, dataBinding: t.path ?? "/" } };
  }
  return children;
}

/** Return true if the batch contains v0.9-format messages. */
export function isV09Batch(messages: unknown[]): boolean {
  return messages.some((m) => {
    const msg = m as Record<string, unknown>;
    return (
      msg.version === "v0.9" ||
      "createSurface" in msg ||
      "updateComponents" in msg
    );
  });
}

/**
 * Translate a v0.9 message batch to v0.8 format.
 *
 * v0.8 ordering rule: deletions → surfaceUpdate → dataModelUpdate → beginRendering.
 */
export function translateV09ToV08(messages: unknown[]): unknown[] {
  const deletions: unknown[] = [];
  const surfaceUpdates: unknown[] = [];
  const dataModelUpdates: unknown[] = [];
  const surfacesWithRoot = new Set<string>();

  for (const msg of messages) {
    const m = msg as V09Message;

    if (m.deleteSurface) {
      deletions.push({ deleteSurface: m.deleteSurface });
      continue;
    }

    // createSurface has no direct v0.8 equivalent — surface is implicitly
    // created by the surfaceUpdate that follows.
    if (m.createSurface) continue;

    if (m.updateComponents) {
      const { surfaceId, components } = m.updateComponents;
      const v08Components = components.map(({ id, component, ...props }) => {
        // Map v0.9 component names to v0.8 equivalents
        const v08Component = component === "ChoicePicker" ? "MultipleChoice" : component;
        const translated: Record<string, unknown> = {};
        // `weight` and `accessibility` are top-level node properties in v0.8 — do not nest them
        const topLevel: Record<string, unknown> = {};
        for (const [k, v] of Object.entries(props)) {
          if (k === "weight" || k === "accessibility") {
            topLevel[k] = v;
          } else if (k === "children") {
            translated[k] = translateChildren(v);
          } else if (k === "variant" && v08Component === "Text") {
            // v0.9 Text uses `variant`, v0.8 uses `usageHint`
            translated["usageHint"] = v;
          } else if (k === "value" && v08Component === "TextField") {
            // v0.9 TextField uses `value`, v0.8 uses `text`
            translated["text"] = v;
          } else if (k === "label" && v08Component === "MultipleChoice") {
            // v0.9 ChoicePicker uses `label`, v0.8 MultipleChoice uses `description`
            translated["description"] = v;
          } else {
            translated[k] = v;
          }
        }
        return { id, ...topLevel, component: { [v08Component]: translated } };
      });
      surfaceUpdates.push({ surfaceUpdate: { surfaceId, components: v08Components } });
      if (components.some((c) => c.id === "root")) {
        surfacesWithRoot.add(surfaceId);
      }
    }

    if (m.updateDataModel) {
      const { surfaceId, path, value } = m.updateDataModel;
      const prefix =
        path && path !== "/" ? path.replace(/^\//, "").replace(/\//g, ".") : "";
      const contents = flattenToV08Contents(value, prefix);
      dataModelUpdates.push({ dataModelUpdate: { surfaceId, contents } });
    }
  }

  return [
    ...deletions,
    ...surfaceUpdates,
    ...dataModelUpdates,
    ...[...surfacesWithRoot].map((surfaceId) => ({
      beginRendering: { surfaceId, root: "root" },
    })),
  ];
}
