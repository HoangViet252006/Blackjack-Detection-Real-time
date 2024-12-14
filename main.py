import argparse
import card_detections
from player_logic import *
import cv2


def get_args():
    parser = argparse.ArgumentParser(description="Card video")
    parser.add_argument("--intput_video_path", "-i", type=str, required=True)
    parser.add_argument("--output_video_path", "-o", type=str, required=True)
    args = parser.parse_args()
    return args

def main(args):
    # Open video

    if args.intput_video_path == '0':
        cap = cv2.VideoCapture(0)
    else:
        cap = cv2.VideoCapture(args.intput_video_path)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(args.output_video_path , fourcc, 30, (width, height))

    is_dealer = False
    id_dealer = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        card_detection = card_detections.Card_detections(MODEL_PATH)
        card_dict = card_detection.detection(frame)
        # reset game
        if len(card_dict) == 0:
            is_dealer = False
            id_dealer = 0
        frame = card_detection.drawing_bounding_box(frame, card_dict)
        # Group and find dealer
        players, id_player = group_cards_by_players(card_dict, DISTANCE_THRESHOLD)
        if not is_dealer:
            is_dealer, id_dealer = find_dealer_card(card_dict, id_player)
        draw_players_with_points(frame, players, is_dealer, id_dealer)

        cv2.imshow("output", frame)
        k = cv2.waitKey(1)
        if k == ord('q'):
            break
        out.write(frame)

    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    args = get_args()
    main(args)