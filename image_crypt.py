import streamlit as st
from PIL import Image

# 1.
def encode_message(message: str) -> list:
    bit_sequence = ""
    for char in message:
        # convert each char to its ascii value in binary format
        binary_char = bin(ord(char))[2:]
        # fill spaces to keep sequence in 8 bit intervals
        binary_char = binary_char.zfill(8)
        # add the bits to the sequence
        bit_sequence += binary_char
    # a sequence of eight one's indicates the end of the message when decoding
    bit_sequence += "11111111"
    # convert to list
    bits = [int(char) for char in bit_sequence]
    return bits

#2.
def encrypt_image(image: Image, bits: list) -> Image:
    width, height = image.size
    # create a new blank image
    new_image = Image.new("RGB", (width, height))
    # iterate over every pixel of the image
    for x in range(width):
        for y in range(height):
            pixel = image.getpixel((x, y))
            # create color
            new_pixel = []
            for i in range(3):
                # as long as there are bits left use them to alter the pixels
                if len(bits) > 0:
                    new_pixel.append(evenodd(pixel[i], int(bits.pop(0))))
                # use the original color values if there are no more bits in the sequence
                else:
                    new_pixel.append(pixel[i])
            new_image.putpixel((x, y), tuple(new_pixel))
    return new_image


def evenodd(original: int, bit: int) -> int:
    if original % 2 != bit % 2:
        # catch edge-case
        if original == 255:
            original -= 1
        else:
            original += 1
    return original

# 3.
def decrypt_image(image: Image) -> list:
    width, height = image.size
    new_bits = []
    for x in range(width):
        for y in range(height):
            pixel = image.getpixel((x, y))
            for value in pixel:
                new_bits.append(value % 2)
    return new_bits

# 4.
def decode_message(bits: list) -> str:
    # converting to string requires chunks of 8 bits but the image propably has an amount of bits not dividable by 8
    remaining_bits = len(bits) % 8
    # cut the last bits to make it dividable by 8
    bits = bits[:len(bits) - remaining_bits]
    # split the list into chunks of 8
    chunks = [bits[i:i+8] for i in range(0, len(bits), 8)]
    # convert every chunk to a char until one chunk consists of only 1s
    characters = []
    for chunk in chunks:
        if chunk == [1, 1, 1, 1, 1, 1, 1, 1]:
            break
        binary = ''.join(map(str, chunk))
        ascii = int(binary, 2)
        characters.append(chr(ascii))
    decoded_string = ''.join(characters)
    return decoded_string

def main():
    st.title("ImageCrypt")

    with st.expander("Encrypt", False):
        upload = st.file_uploader("Choose image to encrypt!", type=["png"])
        if upload is not None:
            # open the uploaded image with PIL
            image = Image.open(upload)

            # calculate maximum message length (pixel has 3 channels, char needs 8 bit, one 'char' is used for signaling end of message)
            char_limit = int(image.size[0] * image.size[1] * 3 / 8) - 1
            text_input = st.text_input("Message", max_chars=char_limit)

            # start encoding
            if st.button("Encode") and text_input != "":
                bits = encode_message(text_input)
                cipher_image = encrypt_image(image, bits)
                cipher_image.save("temp.png", "PNG")
                st.download_button(
                    label="Download encrypted image",
                    data=open("temp.png", "rb").read(),
                    file_name="temp.png"
                )

    with st.expander("Decrypt", False):
        upload = st.file_uploader("Choose image to decrypt!", type=["png"])
        if upload is not None:
            # open the uploaded image with PIL
            image = Image.open(upload)

            # decrypt image
            bits = decrypt_image(image)
            text = decode_message(bits)
            st.text_area("Decoded message", value=text)





if __name__ == "__main__":
    main()