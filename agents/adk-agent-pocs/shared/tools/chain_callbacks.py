def chain_callbacks(*callbacks):
    """Run callbacks in order, threading each result into the next."""

    def combined(callback_context, llm_response):
        result = llm_response
        for cb in callbacks:
            outcome = cb(callback_context, result)
            if outcome is not None:
                result = outcome
        return result

    return combined
