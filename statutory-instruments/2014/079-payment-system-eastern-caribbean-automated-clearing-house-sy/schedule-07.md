SCHEDULE 2
(rules (31, 89, 91)
IMAGE QUALITY SPECIFICATIONS
    (1) A system participant shall perform image quality checks for
each set of image view records (Type 50, Type 52 and Type 54) as set
out in the ANSI X9.100-187 Standards. The full details fordata and
field specifications may be found in section 5 of the ANSI X9.100-187
Standards.
    (2) Where a system participant fails to follow the data and field
specifications the operator or the receiving participant may reject the
item or file.
    (3) All image items deposited as part of an image cash letter shall
meet the criteria set out in Table A and Table B.

Table A - Image Standard
Physical Cheque
Canadian Payment Association Code 006
Standard
Image Cash Letter
ANSI X9.100-187 Standards
Image Format
TIFF 6.0 CCITT Group 4
Image Quality / Compression
200 or 240 dpi
TIFF TAG Byte Order
Little Endian (Intel) byte order
Variable Record Length Indicator
Big Endian (Motorola) byte order
Character Code
8-bit EBCDIC
View Descriptor
Full view, i.e., no partial views
View
Bi-tonal front and bi-tonal rear (Black and
White)
Maximum File Size
Limit outward clearing file size to 5MB
Table B – Image Quality Assurance (IQA) Settings
Length
Height
Corners
Minimum = 6.25 Inches
Minimum = 2.75 Inches
Maximum = 8.50 Inches
Maximum = 3.75 Inches
Front Lower Right and Back Lower Left Corners > 0.8 Inches
Front Upper (both) and Front Lower Left Corners > 1.0 Inches
Rear Upper (both) and Rear Lower Right Corners > 3.0 Inches
Document Skew
Front Skew > 287.2 Degrees
Darkness
Front Minimum Darkness < 0.009 (Ratio of black pixels to
total pixels)
Front Maximum Darkness > 0.9 (Ratio of black pixels to total
pixels)
Back Minimum Darkness < 0.0038 (Ratio of black pixels to
total pixels)
Back Maximum Darkness > 0.98 (Ratio of black pixels to total
pixels)
Noise
Front Noise Relative Density (Black and White)
> 5,852 Spots considered as noise per square inch, on average
Back Noise Relative Density (Black and White)
> 5,852 Spots considered as noise per square inch, on average
IQA Record Size
Front = Minimum 250 Bytes, Maximum 200,000 Bytes
Back = Minimum 250 Bytes, Maximum 200,000 Bytes
