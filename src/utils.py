def distance(p1, p2):
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

def get_center_box(bbox):
    x1, y1, x2, y2 = map(int, bbox)
    x_center = (x1 + x2) / 2
    y_center = (y1 + y2) / 2
    return (x_center, y_center)

def calculate_point(cards):
    point = 0
    count_A = 0
    for card in cards:
        card = card[:-1] if len(card) > 1 else card
        if card == "A":
            point += 11
            count_A += 1
        elif card in "JQK":
            point += 10
        else:
            point += int(card)

        if point > 21 and count_A > 0:
            point -= 10
            count_A -= 1

    return point
