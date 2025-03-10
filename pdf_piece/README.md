### PDF piece module
1. define the object class input and output address
   You can modify the detect_config.yaml under ./cfg dir or modufy the override dictionary

#### general detection
2. find the drawing area, title block area, tables and text boxes on blue prints. The output is .json format
   1. title_detect: parse out the information inside of the title block
   2. drawing_detect: running detailed dection on the drawing area for target objects
   3. parse_table:Parse table from PDF and then gird table using CV2 run pytasseract OCR to extract the content 

#### medium detection
the specific module that deal with very big pictures, tile into smaller pieces as 5000X5000

