"""
This script fixes a Maya 2020 crash issue that occurs when closing the application
after opening a scene file through Python API calls (cmds.file) instead of through UI.
The crash is caused by uninitialized internal UI variables related to the
'uiConfigurationScriptNode' when files are loaded asynchronously in Viewport 2.0.

The script scans Maya ASCII (.ma) files, finds and clears the value of the
'uiConfigurationScriptNode' node to prevent Maya from crashing on exit.

This modification does not affect any scene data and is automatically restored
when the scene is reopened.

Author: Davina Ma Heming
Date: 2026.04.22
Environment: Python 2.7
"""

import os
import re
import io
import chardet


# This function is the same as in py27-utils/encode_decode_utils.py.
def detect_encoding(text):
	"""
	Detect text encoding method.
    This function may make mistakes if the given text length is too short.
	
	:type text: unicode or str
	:rtype: string    # "unicode" / "utf-8" / "gbk" / "GB2312"
	"""
	if isinstance(text, unicode):
		return "unicode"
	detected = chardet.detect(text)
	
	# If chardet has a result, return the guessed result
	if detected.get("encoding"):
		return detected["encoding"].lower()
	# If chardet does not have a result, try decoding from provided decode methods
	else:
		for enc in ["utf-8", "gbk", "big5"]:
			try:
				text.decode(enc)
			except UnicodeDecodeError:
				continue
			else:
				return enc
	return ""


def reset_uiConfigurationScriptNode(ma_file_path):
    """
    Reset uiConfigurationScriptNode value in .ma file to empty
    :type ma_file_path: str
    :rtype: bool    # edit success or not
    """
    if not ma_file_path or not os.path.exists(ma_file_path):
        raise IOError(u"ma_file_path not exists: %s"%ma_file_path)
    
    temp_path = ma_file_path + ".tmp"

    # Regex pattern for Maya UI config string block
    pattern = re.compile(r"""
        (                               # 捕获组开始
        ^[\s\t]*                        # 行首允许有空格或tab
        setAttr\s+                      # 匹配 "setAttr" 后面至少一个空白
        "\.b"                           # 精确匹配属性名 ".b" （点号要转义）
        \s+-type\s+"string"\s*          # 匹配 -type "string"
        \(                              # 匹配左括号 (
        \s*                             # 括号后可能还有换行或空白
        "//\s+Maya\s+Mel\s+UI\s+Configuration\s+File\.\\n//\\n//\s+This\s+script\s+is\s+machine\s+generated\.\s+Edit\s+at\s+your\s+own\s+risk\.     # 匹配最前面的注释字符串
        .*                              # 匹配中间的所有Maya代码
        "\)                             # 匹配右引号 " 和右括号 )
        ;                               # 匹配分号 ;
        )                               # 捕获组结束
        \s*setAttr\s+"\.st"\s+3         # 匹配结尾的转行符和 setAttr ".st" 3
    """, flags=re.VERBOSE | re.MULTILINE | re.DOTALL)

    chunk_size = 1024*1024  # 1MB read buffer
    keep_len = 2000     # keep last bytes to avoid cutting the pattern in half

    buffer = ""
    has_match = False

    try:
        with io.open(ma_file_path, 'r', encoding='GB2312', errors="ignore") as src, \
            io.open(temp_path, 'w', encoding='GB2312') as dst:
			
            while True:
                chunk = src.read(chunk_size)
                if not chunk:
                    break
                buffer += chunk

                # keep tail to catch cross-boundary regex
                process_part = buffer[:-keep_len]
                buffer = buffer[-keep_len:]

                matches = pattern.findall(process_part)
                if matches:
                    has_match = True
                    for match_obj_group1 in matches:
                        process_part = process_part.replace(match_obj_group1, '\tsetAttr ".b" -type "string" "";')

                dst.write(process_part)

            # Process the remaining buffer
            matches = pattern.findall(buffer)
            if matches:
                has_match = True
                for match_obj_group1 in matches:
                    buffer = buffer.replace(match_obj_group1, '\tsetAttr ".b" -type "string" "";')

            dst.write(buffer)
    
        if has_match:
            # replace original file safely
            os.remove(ma_file_path)
            os.rename(temp_path, ma_file_path)
        else:
            # remove tmp file
            os.remove(temp_path)
            return False

    except:
        raise

    return True


ma_file_path = "path/to/your/scene.ma"   # TODO: set your .ma file path here
if __name__ == "__main__":
    try:
        reset_uiConfigurationScriptNode(ma_file_path)
        print("uiConfigurationScriptNode reset successfully.")
    except Exception as e:
        print("Error resetting uiConfigurationScriptNode: %s"%str(e))