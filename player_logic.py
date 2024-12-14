import cv2
from src.utils import distance, calculate_point, get_center_box
from src.config import *

def draw_bounding_box_and_label(frame, bbox, label, color):
    x1, y1, x2, y2 = map(int, bbox)
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    cv2.putText(frame, label, (x1, y2 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)


def calculate_player_bounding_box_and_cards(player_boxes):
    min_x, min_y, max_x, max_y = float('inf'), float('inf'), 0, 0
    detected_cards = []

    for box_data in player_boxes:
        card_name, bbox = box_data
        x1, y1, x2, y2 = map(int, bbox)
        min_x = min(min_x, x1)
        max_x = max(max_x, x2)
        min_y = min(min_y, y1)
        max_y = max(max_y, y2)
        detected_cards.append(card_name)

    return detected_cards, (min_x, min_y, max_x, max_y)


def add_card_to_player(player_cards_bbox, player_id, card_name, bounding_box):
    if player_id not in player_cards_bbox:
        player_cards_bbox[player_id] = []  # Initialize the player's group if not present
    player_cards_bbox[player_id].append((card_name, bounding_box))


def group_cards_by_players(card_dict, distance_threshold):
    list_card = [[cls_name, bbox] for cls_name, bbox in card_dict.items()]
    card_belong_player = {}
    player_cards_bbox = {}

    for idx1 in range(len(list_card)):
        for idx2 in range(idx1 + 1, len(list_card)):
            box1 = list_card[idx1][1]
            box2 = list_card[idx2][1]
            p1 = get_center_box(box1)
            p2 = get_center_box(box2)
            distance_between_boxes = distance(p1, p2)
            if distance_between_boxes < distance_threshold:
                card_name_1 = list_card[idx1][0]
                card_name_2 = list_card[idx2][0]

                card1_is_mapped = card_name_1 in card_belong_player
                card2_is_mapped = card_name_2 in card_belong_player

                if card_name_1 not in card_belong_player:
                    if card_name_2 not in card_belong_player:
                        card_belong_player[card_name_1] = card_belong_player[card_name_2] = len(card_belong_player)
                    else:
                        card_belong_player[card_name_1] = card_belong_player[card_name_2]
                else:
                    if card_name_2 not in card_belong_player:
                        card_belong_player[card_name_2] = card_belong_player[card_name_1]

                if not card1_is_mapped:
                    add_card_to_player(player_cards_bbox, card_belong_player[card_name_1], card_name_1, box1)

                if not card2_is_mapped:
                    add_card_to_player(player_cards_bbox, card_belong_player[card_name_2], card_name_2, box2)

    return player_cards_bbox, card_belong_player


def draw_players_with_points(frame, player_groups, has_dealer, dealer_card_id):
    if has_dealer:
        dealer_points = 0
        len_dealer = 0
        # Draw bounding box for the dealer
        for player_id, player_boxes in player_groups.items():
            player_cards, bbox_dealer  = calculate_player_bounding_box_and_cards(player_boxes)
            player_points = calculate_point(player_cards)
            color = (255, 255, 255)
            if dealer_card_id in player_cards:
                dealer_points = player_points
                len_dealer = len(player_cards)
                label = f"Dealer: {dealer_points}"
                draw_bounding_box_and_label(frame, bbox_dealer, label, color)
                break
        # Draw bounding box for other players
        for idx, (player_id, player_boxes) in enumerate(player_groups.items()):
            player_cards, bbox_player = calculate_player_bounding_box_and_cards(player_boxes)
            player_points = calculate_point(player_cards)
            if dealer_card_id not in player_cards:
                label = f"Player_{idx}: {player_points}"
                result_color = (255, 255, 255)
                if dealer_points > 16:
                    if (player_points > dealer_points and player_points <= 21) or (player_points == 21 and len(player_cards) == 2):
                        result_color = WIN_COLOUR
                    elif (player_points > 21) or (player_points < dealer_points) or (dealer_points == 21 and len_dealer == 2):
                        result_color = LOSE_COLOUR
                    else:
                        result_color = DRAW_COLOUR

                draw_bounding_box_and_label(frame, bbox_player, label, result_color)
    else:
        for idx, (player_id, player_boxes) in enumerate(player_groups.items()):
            player_cards, bbox_player = calculate_player_bounding_box_and_cards(player_boxes)
            player_points = calculate_point(player_cards)
            label = f"Player_{idx}: {player_points}"
            color = (255, 255, 255)
            draw_bounding_box_and_label(frame, bbox_player, label, color)


def find_dealer_card(card_dict, card_to_player_map):
    has_dealer = False
    dealer_card_id = -1

    if len(card_dict) <= 1:
        return False, -1

    dealer_candidates = []
    for card_name, bbox in card_dict.items():
        if card_name not in card_to_player_map:
            dealer_candidates.append(card_name)
            if len(dealer_candidates) > 1:
                return False, -1


    if len(dealer_candidates) == 1:
        has_dealer = True
        dealer_card_id = dealer_candidates[0]

    return has_dealer, dealer_card_id
