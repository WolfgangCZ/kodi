from passlib.hash import md5_crypt

def hash_md5_file(file_name: str):
    file = open(file_name, 'rb')
    md5 = md5_crypt.hash(file.read())
    new_name = file_name + '.md5'
    open(new_name, 'w').write(md5)

if __name__ == "__main__":
    hash_md5_file('addons.xml')