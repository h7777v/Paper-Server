def render(template: str, context: dict) -> str:
    out = []
    i = 0
    n = len(template)

    while i < n:
        start = template.find("<ssr:placeholder", i)
        if start == -1:
            out.append(template[i:])
            break

        # copy everything before the tag
        out.append(template[i:start])

        # find end of opening tag
        end = template.find(">", start)
        if end == -1:
            out.append(template[start:])
            break

        tag = template[start:end+1]

        # extract name="..."
        name_pos = tag.find('name="')
        if name_pos == -1:
            # malformed, skip
            i = end + 1
            continue

        name_start = name_pos + len('name="')
        name_end = tag.find('"', name_start)
        name = tag[name_start:name_end]

        # find closing tag
        close = template.find("</ssr:placeholder>", end)
        if close == -1:
            # malformed, skip
            i = end + 1
            continue

        # if context has the key → replace
        if name in context:
            out.append(str(context[name]))
        else:
            # no value → remove placeholder entirely
            # (append nothing)
            pass

        # move pointer past closing tag
        i = close + len("</ssr:placeholder>")

    return "".join(out)