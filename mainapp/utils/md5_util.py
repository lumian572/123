# mainapp/utils/md5_util.py
import hashlib

def md5(password: str) -> str:
    """对密码进行MD5加密"""
    if not isinstance(password, str):
        password = str(password)
    md5_obj = hashlib.md5()
    md5_obj.update(password.encode('utf-8'))
    return md5_obj.hexdigest()