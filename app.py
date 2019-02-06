from flask import Flask, jsonify, request
from flask.json import JSONEncoder

class CustomJSONEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, set):
            return list(o)

        return JSONEncoder.default()

app = Flask(__name__)
app.users = {}
app.id_count = 1
app.tweets = []
app.json_encoder = CustomJSONEncoder

@app.route("/ping", methods=['GET'])
def ping():
    return "pong"


@app.route("/sign-up", methods=['POST'])
def sign_up():
    new_user                = request.json
    new_user["id"]          = app.id_count
    app.users[app.id_count] = new_user
    app.id_count            = app.id_count + 1

    return jsonify(new_user)


@app.route('/tweet', methods=['POST'])
def tweet():
    payload = request.json
    user_id = int(payload['id'])
    tweet = payload['tweet']

    if user_id not in app.users:
        return '사용자가 존재하지 않습니다', 400

    if len(tweet) > 300:
        return '300자를 초과했습니다', 400

    user_id = int(payload['id'])

    app.tweets.append({
        'user_id' : user_id,
        'tweet' : tweet
    })

    return '', 200


@app.route('/follow', methods=['POST'])
def follow():
    payload = request.json
    user_id = int(payload['id'])
    user_id_to_follow = int(payload['follow'])

    if user_id not in app.users or user_id_to_follow not in app.users:
        return '사용자가 존재하지 않습니다', 400

    user = app.users[user_id]
    user.setdefault('follow', set()).add(user_id_to_follow)

    return jsonify(user)


@app.route('/unfollow', methods=['POST'])
def unfollow():
    payload = request.json
    user_id = int(payload['id'])
    user_id_to_follow = int(payload['unfollow'])

    if user_id not in app.users or user_id_to_follow not in app.users:
        return '사용자가 존재하지 않습니다', 400

    user = app.users[user_id]
    user.setdefault('follow', set()).discard(user_id_to_follow)

    return jsonify(user)


@app.route('/timeline/<int:user_id>', methods=['GET'])
def timeline(user_id):
    if user_id not in app.users:
        return '사용자가 존재하지 않습니다', 400

    follow_list = app.users[user_id].get('follow', set())
    follow_list.add(user_id)
    timeline = [tweet for tweet in app.tweets if tweet['user_id'] in follow_list]

    return jsonify({
        'user_id' : user_id,
        'timeline' : timeline
    })


'''
http -v GET http://localhost:5000/ping
http -v POST http://localhost:5000/sign-up name=이대섭 email=daeseob.lee@gmail.com password=test1234
http -v POST http://localhost:5000/sign-up name=홍길동 email=a.lee@gmail.com password=test1234
http -v POST http://localhost:5000/tweet id:=1 tweet="My First Tweet"
http -v POST http://localhost:5000/tweet id:=2 tweet="두번재 트윗입니당"
http -v POST http://localhost:5000/follow id:=1 follow:=2
http -v GET http://localhost:500/timeline/1

'''
if __name__ == '__main__':
    app.run()