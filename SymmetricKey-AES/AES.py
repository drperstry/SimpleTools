from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Util.Padding import pad
import argparse
import textwrap


def AES_Encrypt(key, Plain, Cipher="./Question2/SymmetricKey-AES/Cipher.txt"):
    
    if(not isinstance(key, bytes)):
        key=key.encode()
    
    if(len(key)!=16):
        return 'key should be of size 16 bits'
    
    try:
        with open(Plain,'rb') as f:
            plaintext= f.read()
    except:
        return 'Plaintext file is not found'
    
    #setup the AES block for Encryption, and setting mode to CBC
    cipher=AES.new(key, AES.MODE_CBC)
    
    #here padding using 'pkcs7' algorithm before encryption
    ciphertext= cipher.encrypt(pad(plaintext,AES.block_size))
    
    #write the iv and ciphertext in the output file
    with open(Cipher, 'wb') as f:
        f.write(cipher.iv)
        f.write(ciphertext)

    return 'Done Encryption'


def AES_Decrypt(key, Cipher, Plain="./Question2/SymmetricKey-AES/Plain.txt"):
    
    if(not isinstance(key, bytes)):
        key=key.encode()
    
    if(len(key)!=16):
        return 'key should be of size 16 bits'

    try:
        with open(Cipher,'rb') as f:
            ivectov=f.read(16)
            ciphertext= f.read()
    except:
        return 'Ciphertext file is not found or having an issue, make sure you encrypted using the same script'
    
    #setup the AES block for decryption, and passing ivectov and setting mode to CBC
    cipher=AES.new(key, AES.MODE_CBC, ivectov)

    #here padding using 'pkcs7' algorithm after encryption
    plaintext= unpad(cipher.decrypt(ciphertext), AES.block_size)
    
    #write the iv and ciphertext in the output file
    with open(Plain, 'wb') as f:
        f.write(plaintext)
    
    return 'Done Decryption'


def main():
    desc=textwrap.dedent('''AES:
            Encryption/Decryption file using Symmetric Key (AES)
            [opts means optional]
            usage:
                1: python AES.py Encrypt [-h] --key 16bit-Key --Plain Plain.txt [opts] --Cipher Cipher.txt
                2: python AES.py Decrypt [-h] --key 16bit-Key --Cipher Cipher.txt [opts] --Plain Plain.txt''')
                
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=desc)
    subparser=parser.add_subparsers(dest='Command')
    Encrypt=subparser.add_parser('Encrypt')
    Decrypt=subparser.add_parser('Decrypt')

    Encrypt.add_argument("--Plain", '-P',type=str, help="--Plain Plain.txt", required=True)
    Encrypt.add_argument("--Cipher", '-C',type=str, help="--Cipher Cipher.txt", required=False)
    Encrypt.add_argument("--Key", '-K',type=str, help="--key 16bit-Key", required=True)
    
    Decrypt.add_argument("--Plain", '-P',type=str, help="--Plain Plain.txt", required=False)
    Decrypt.add_argument("--Cipher", '-C',type=str, help="--Cipher Cipher.txt", required=True)
    Decrypt.add_argument("--Key", '-K',type=str, help="--key 16bit-Key", required=True)

    args = parser.parse_args()

    if args.Command == None:
        print("choose one of those commands [Encrypt, Decrypt]")
    elif args.Command == 'Encrypt':
        if(args.Cipher):
            print(AES_Encrypt(args.Key, args.Plain, args.Cipher))
        else:
            print(AES_Encrypt(args.Key, args.Plain))
    elif args.Command == 'Decrypt':
        if(args.Plain):
            print(AES_Decrypt(args.Key, args.Cipher, args.Plain))
        else:
            print(AES_Decrypt(args.Key, args.Cipher))


# Driver Code
if __name__ == '__main__' :
    # Calling main function
    main()