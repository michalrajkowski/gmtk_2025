import argparse
from PIL import Image


def report_size(img: Image.Image) -> None:
    print(f"Current image size: {img.width}×{img.height} pixels")


def resize_image(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    # NEAREST ensures no new colors are introduced
    return img.resize((target_w, target_h), resample=Image.Resampling.NEAREST)


def main():
    p = argparse.ArgumentParser(
        description="Report an image's resolution and resize it with fixed pixels."
    )
    p.add_argument("infile", help="Path to source image")
    p.add_argument("outfile", help="Path to write resized image")
    p.add_argument(
        "--width", "-W", type=int, required=True, help="Target width in pixels"
    )
    p.add_argument(
        "--height", "-H", type=int, required=True, help="Target height in pixels"
    )
    args = p.parse_args()

    img = Image.open(args.infile)
    report_size(img)

    resized = resize_image(img, args.width, args.height)
    resized.save(args.outfile)
    print(f"Saved resized image to {args.outfile} ({args.width}×{args.height})")


if __name__ == "__main__":
    main()
