from flask import Flask, request, jsonify, render_template, redirect, url_for
import json
import os
from datetime import datetime

app = Flask(__name__)

# 数据存储文件
DATA_FILE = 'customer_data.json'

# 确保数据文件存在
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)

def load_data():
    """加载客户数据"""
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    """保存客户数据"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    """主页"""
    return redirect(url_for('static', filename='wuhan_travel_website.html'))

@app.route('/submit-form', methods=['POST'])
def submit_form():
    """处理表单提交"""
    try:
        data = {
            'full_name': request.form.get('full_name', ''),
            'email': request.form.get('email', ''),
            'country': request.form.get('country', ''),
            'interests': request.form.getlist('interests[]'),
            'message': request.form.get('message', ''),
            'submitted_at': datetime.now().isoformat(),
            'ip_address': request.remote_addr
        }
        
        # 验证必填字段
        if not data['full_name'] or not data['email'] or not data['country']:
            return jsonify({'status': 'error', 'message': 'Please fill in all required fields'}), 400
        
        # 加载并保存数据
        customers = load_data()
        customers.append(data)
        save_data(customers)
        
        return jsonify({'status': 'success', 'message': 'Thank you! Your information has been submitted successfully.'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/admin')
def admin_panel():
    """管理员面板"""
    customers = load_data()
    return render_template('admin.html', customers=customers)

@app.route('/admin/export')
def export_data():
    """导出数据"""
    customers = load_data()
    response = app.response_class(
        response=json.dumps(customers, ensure_ascii=False, indent=2),
        status=200,
        mimetype='application/json'
    )
    response.headers["Content-Disposition"] = "attachment; filename=customer_data.json"
    return response

@app.route('/admin/delete/<int:index>')
def delete_customer(index):
    """删除客户数据"""
    customers = load_data()
    if 0 <= index < len(customers):
        deleted = customers.pop(index)
        save_data(customers)
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    # 创建静态文件夹并复制HTML文件
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # 启动服务器，使用端口 5000
    app.run(host='0.0.0.0', port=5000, debug=True)