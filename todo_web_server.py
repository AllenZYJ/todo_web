from flask import Flask, request, jsonify
from flask_cors import CORS
import csv
import json
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

todos = []
def to_utc(date_string):
    date = datetime.fromisoformat(date_string)
    return date.astimezone(timezone.utc).isoformat()

@app.route('/todos/delete_all/<string:date>', methods=['DELETE'])
def delete_todos_by_date(date):
    global todos
    todos_to_delete = []
    for i, todo in enumerate(todos):
        if todo['date'].startswith(date):
            todos_to_delete.append(i)

    if not todos_to_delete:
        return jsonify(warning='No todos found for the specified date.'), 404

    todos_to_delete.reverse()
    for i in todos_to_delete:
        todos.pop(i)
    write_todos(todos)
    return jsonify(success=True)


def read_todos():
    todos = []
    with open('todos.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            index, text, done, date = row
            todos.append({'index': int(index), 'text': text, 'done': json.loads(done.lower()), 'date': date})
        print(todos)
    return todos

def write_todos(todos):
    with open('todos.csv', 'w') as f:
        writer = csv.writer(f)
        for todo in todos:
            writer.writerow([todo['index'], todo['text'], todo['done'], todo['date']])
from datetime import datetime, timedelta
import pytz
@app.route('/csv', methods=['GET'])
def get_csv_data():
    with open('todos.csv', 'r') as f:
        return f.read(), 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/todos', methods=['GET', 'POST'])
def handle_todos():
    global todos
    if request.method == 'POST':
        todo_data = request.get_json()
        # 将待办事项的日期转换为 datetime 对象，并增加 8 小时
        date = datetime.fromisoformat(todo_data['date'].replace('Z', '+00:00'))
        adjusted_date = date + timedelta(hours=8)
        # 将修改后的 datetime 对象转换回 ISO 格式字符串
        adjusted_date_utc = adjusted_date.astimezone(pytz.utc)
        adjusted_date_str = adjusted_date_utc.isoformat().replace('+00:00', 'Z')
        
        todos.append({'index': len(todos), 'text': todo_data['text'], 'done': todo_data['done'], 'date': adjusted_date_str})
        write_todos(todos)
        print(todos)
        return jsonify(success=True)
    else:
        return jsonify(todos=todos)


@app.route('/todos/<int:todo_index>', methods=['PUT'])
def update_todo(todo_index):
    global todos
    todo_data = request.get_json()
    todos[todo_index] = todo_data
    write_todos(todos)
    return jsonify(success=True)

@app.route('/todos/<int:todo_index>', methods=['DELETE'])
def delete_todo(todo_index):
    global todos
    if 0 <= todo_index < len(todos):
        todos.pop(todo_index)
        write_todos(todos)
        return jsonify(success=True)
    else:
        return jsonify(error='Todo not found.'), 404

if __name__ == '__main__':
    try:
        todos = read_todos()
    except FileNotFoundError:
        pass

    app.run(host='0.0.0.0', port=2172)
