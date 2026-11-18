def find_max(scores):
    biggest = scores[0]
    for score in scores[1:]:
        if score > biggest:
            biggest = score
    return biggest


def count_pass(scores, cutoff=60):
    return sum(score >= cutoff for score in scores)