def batch_qs(qs, batch_size=1000):
    # https://djangosnippets.org/snippets/117
    total = qs.count()
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        yield (start, end, total, qs[start:end])
