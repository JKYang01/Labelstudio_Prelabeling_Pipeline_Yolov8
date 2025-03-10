from  pipeline_utils.utils.s3_load import pdf_from_s3
import fitz

def mapping_bbx(rotation,bbx,w,h):
    ## using PyMupdf
    ## mapping the rotated pdf page position to the image standard x,y position 
    ## image standard starting point is from left top
    a0,b0,a1,b1=bbx[0],bbx[1],bbx[2],bbx[3]
    
    if rotation==0:
        x0=a0
        y0=h-b1
        x1=a1
        y1=h-b0
        
    elif rotation==90:
        x0=b1
        y0=a0
        x1=b0
        y1=a1
        
        
    elif rotation==180:
        x0=w-a1
        y0=b0
        x1=w-a0
        y1=b1
    
    elif rotation==270:
        x1=w-b0
        y1=h-a0
        x0=w-b1
        y0=h-a1
        
    return (x0,y0,x1,y1)


def pdf_to_textboxes(pdf_path, page_num,from_s3=True):
    if from_s3:
        pdf_stream = pdf_from_s3(pdf_path)
        # Open the PDF with fitz
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
    else:
        doc = fitz.open(pdf_path)
    # doc = fitz.open(pdf_path)
    page = doc.load_page(page_num)  
    # Get the page dimensions
    width = page.rect.width
    height = page.rect.height
    rotation = page.rotation
    blocks = page.get_text("dict")["blocks"]
    result = {
            'width': int(width),
            'height': int(height),
            'objects': []
        }

    for b in blocks:
        if b['type'] == 0:  # This is a text block
            
            rect = b["bbox"]  # The bounding box
            text = (b["lines"][0]["spans"][0]['text'])
            
            new_rect = mapping_bbx (rotation,rect,width,height)
            
            result['objects'].append({
                'text': text,
                'name': 'text',
                'xmin': int(new_rect[0]),
                'ymin': int(new_rect[1]),
                'xmax': int(new_rect[2]),
                'ymax': int(new_rect[3]),
            })

    doc.close()
    
    return result



if __name__ == '__main__':
    import sys
    data = pdf_to_textboxes(sys.argv[1], sys.argv[2])
    print(data)