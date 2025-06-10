import docx
from docx.oxml.ns import qn
from PIL import Image
import io
import sys
import os


def get_image_ppi(image_data):
    try:
        with Image.open(io.BytesIO(image_data)) as img:
            dpi = img.info.get('dpi')
            if dpi:
                # DPI is a tuple (x_dpi, y_dpi); typically, they are the same for PPI
                return dpi[0]  # Return x_dpi as PPI
            else:
                return None
    except Exception as e:
        print(f"Error processing image: {e}", file=sys.stderr)
        return None


def extract_images_ppi(docx_path):
    try:
        doc = docx.Document(docx_path)
        image_count = 0
        results = []

        # Check for images in the document's inline shapes
        for rel in doc.part.rels.values():
            if "image" in rel.reltype:
                image_count += 1
                image_data = rel.target_part.blob
                ppi = get_image_ppi(image_data)
                results.append((image_count, ppi))

        # Check for images in headers and footers
        for section in doc.sections:
            for header in section.header._element.xpath('.//w:pict'):
                for blip in header.xpath('.//a:blip',
                                         namespaces={'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}):
                    rId = blip.get(qn('r:embed'))
                    if rId:
                        image_part = doc.part.rels[rId].target_part
                        image_count += 1
                        image_data = image_part.blob
                        ppi = get_image_ppi(image_data)
                        results.append((image_count, ppi))

            for footer in section.footer._element.xpath('.//w:pict'):
                for blip in footer.xpath('.//a:blip',
                                         namespaces={'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}):
                    rId = blip.get(qn('r:embed'))
                    if rId:
                        image_part = doc.part.rels[rId].target_part
                        image_count += 1
                        image_data = image_part.blob
                        ppi = get_image_ppi(image_data)
                        results.append((image_count, ppi))

        # Print results
        if image_count == 0:
            print("No images found in the document.")
        else:
            print(f"Found {image_count} images in the document.")
            for img_num, ppi in results:
                if ppi is not None:
                    print(f"Image {img_num}: PPI = {ppi}")
                else:
                    print(f"Image {img_num}: PPI not available (no DPI metadata)")

    except FileNotFoundError:
        print(f"Error: The file '{docx_path}' was not found.", file=sys.stderr)
    except Exception as e:
        print(f"Error processing document: {e}", file=sys.stderr)


def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_image_ppi.py <path_to_docx>")
        sys.exit(1)

    docx_path = sys.argv[1]
    if not os.path.splitext(docx_path)[1].lower() == '.docx':
        print("Error: Please provide a .docx file.", file=sys.stderr)
        sys.exit(1)

    extract_images_ppi(docx_path)


if __name__ == "__main__":
    main()