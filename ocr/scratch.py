from flask import Flask, request, jsonify
from paddleocr import PaddleOCR
import fitz  # PyMuPDF
import os
import tempfile

# 初始化 Flask 应用
app = Flask(__name__)

# 初始化 PaddleOCR（支持中文）
ocr = PaddleOCR(use_angle_cls=True, lang='ch')

def pdf_to_images(pdf_path, dpi=150):
    """ 将 PDF 转换为图像列表 """
    doc = fitz.open(pdf_path)
    images = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=dpi)
        img_path = os.path.join(tempfile.gettempdir(), f"page_{page_num}.png")
        pix.save(img_path)
        images.append(img_path)
    return images

@app.route('/ocr', methods=['POST'])
def ocr_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    # 保存上传的 PDF 到临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmpfile:
        file.save(tmpfile.name)
        pdf_path = tmpfile.name

    try:
        # Step 1: 将 PDF 转换为图像
        image_paths = pdf_to_images(pdf_path)

        # Step 2: 对每张图像进行 OCR
        full_text = ""
        for img_path in image_paths:
            result = ocr.ocr(img_path, cls=True)
            for line in result:
                for word in line:
                    full_text += word[1][0] + " "
            full_text += "\n"

        # 返回提取出的文本
        return jsonify({
            "text": full_text.strip()
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # 清理临时文件
        os.unlink(pdf_path)
        for img in image_paths:
            os.remove(img)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)