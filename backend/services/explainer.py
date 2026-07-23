def generate_explanation(results):

    if not results:
        return "No evidence was found."

    supports = [
        r["title"]
        for r in results
        if r["label"] == "supports claim"
    ]

    contradicts = [
        r["title"]
        for r in results
        if r["label"] == "contradicts claim"
    ]

    if len(supports) > len(contradicts):

        return (
            f"The claim is supported by "
            f"{len(supports)} news source(s). "
            f"No significant contradicting evidence "
            f"was found."
        )

    elif len(contradicts) > len(supports):

        return (
            f"The claim is contradicted by "
            f"{len(contradicts)} news source(s)."
        )

    return (
        "Available evidence is mixed or inconclusive."
    )