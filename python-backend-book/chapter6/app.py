from flask      import Flask, request, jsonify, current_app
from flask.json import JSONEncoder
from sqlalchemy import create_engine, text

## Default JSON encoder는 set를 JSON으로 변환할 수 없다.
## 그럼으로 커스텀 엔코더를 작성해서 set을 list로 변환하여
## JSON으로 변환 가능하게 해주어야 한다.
class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)

        return JSONEncoder.default(self, obj)

def get_user(user_id):
    user = current_app.database.execute(text("""
        SELECT 
            id,
            name,
            email,
            profile
        FROM users
        WHERE id = :user_id
    """), {
        'user_id' : user_id 
    }).fetchone()

    return {
        'id'      : user['id'],
        'name'    : user['name'],
        'email'   : user['email'],
        'profile' : user['profile']
    } if user else None

def insert_user(user):
    return current_app.database.execute(text("""
        INSERT INTO users (
            name,
            email,
            profile,
            hashed_password
        ) VALUES (
            :name,
            :email,
            :profile,
            :password
        )
    """), user).lastrowid

def insert_tweet(user_tweet):
    return current_app.database.execute(text("""
        INSERT INTO tweets (
            user_id,
            tweet
        ) VALUES (
            :id,
            :tweet
        )
    """), user_tweet).rowcount

def insert_follow(user_follow):
    return current_app.database.execute(text("""
        INSERT INTO users_follow_list (
            user_id,
            follow_user_id
        ) VALUES (
            :id,
            :follow
        )
    """), user_follow).rowcount

def insert_unfollow(user_unfollow):
    return current_app.database.execute(text("""
        DELETE FROM users_follow_list
        WHERE user_id = :id
        AND follow_user_id = :unfollow
    """), user_unfollow).rowcount

def get_timeline(user_id):
    timeline = current_app.database.execute(text("""
        SELECT 
            t.user_id,
            t.tweet
        FROM tweets t
        LEFT JOIN users_follow_list ufl ON ufl.user_id = :user_id
        WHERE t.user_id = :user_id 
        OR t.user_id = ufl.follow_user_id
    """), {
        'user_id' : user_id 
    }).fetchall()

    return [{
        'user_id' : tweet['user_id'],
        'tweet'   : tweet['tweet']
    } for tweet in timeline]

def create_app(test_config = None):
    app = Flask(__name__)

    app.json_encoder = CustomJSONEncoder

    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.update(test_config)

    database     = create_engine(app.config['DB_URL'], encoding = 'utf-8', max_overflow = 0)
    app.database = database

    @app.route("/ping", methods=['GET'])
    def ping():
        return "pong"

    @app.route("/sign-up", methods=['POST'])
    def sign_up():
        new_user    = request.json
        new_user_id = insert_user(new_user)
        new_user    = get_user(new_user_id)

        return jsonify(new_user)

    @app.route('/tweet', methods=['POST'])
    def tweet():
        user_tweet = request.json
        tweet      = user_tweet['tweet']

        if len(tweet) > 300:
            return '300자를 초과했습니다', 400

        insert_tweet(user_tweet)

        return '', 200

    @app.route('/follow', methods=['POST'])
    def follow():
        payload = request.json
        insert_follow(payload) 

        return '', 200

    @app.route('/unfollow', methods=['POST'])
    def unfollow():
        payload = request.json
        insert_unfollow(payload)

        return '', 200

    @app.route('/timeline/<int:user_id>', methods=['GET'])
    def timeline(user_id):
        return jsonify({
            'user_id'  : user_id,
            'timeline' : get_timeline(user_id)
        })

    return app

'''
http -v POST "http://localhost:5000/sign-up" \
    name=송은우 \
    email=songe@gmail.com   \
    password=test1234   \
    profile='profile 1'
    
http -v POST "http://localhost:5000/sign-up" \
    name=이대섭 \
    email=aaaa@gmail.com   \
    password=test1234   \
    profile='profile Hello world'
    
http -v POST "http://localhost:5000/sign-up" \
    name=홍길동 \
    email=bbbb@gmail.com   \
    password=test1234   \
    profile='좋네요 반갑습니다'


http -v POST "http://localhost:5000/sign-up" \
    name=코난 \
    email=ccc@gmail.com   \
    password=test1234   \
    profile='ㅋㅋㅋ 반갑습니다'


http -v POST localhost:5000/tweet id=1 tweet='Hello World'    
http -v POST localhost:5000/tweet id=2 tweet='좋네요1'
http -v POST localhost:5000/tweet id=3 tweet='기분이 최고2'
http -v POST localhost:5000/tweet id=4 tweet='오늘도 좋은날3'

http -v POST http://localhost:5000/follow id:=2 follow:=1
http -v POST http://localhost:5000/follow id:=3 follow:=1
http -v POST http://localhost:5000/follow id:=4 follow:=1

http -v POST http://localhost:5000/follow id:=1 follow:=2
http -v POST http://localhost:5000/follow id:=3 follow:=2

http -v POST http://localhost:5000/unfollow id:=1 unfollow:=2
http -v POST http://localhost:5000/unfollow id:=1 unfollow:=3
http -v POST http://localhost:5000/unfollow id:=1 unfollow:=4
http -v POST http://localhost:5000/unfollow id:=2 unfollow:=3
http -v POST http://localhost:5000/unfollow id:=2 unfollow:=4

http -v GET localhost:5000/timeline/1
http -v GET localhost:5000/timeline/2
    
'''
if __name__ == '__main__':
    app = create_app()
    app.run()