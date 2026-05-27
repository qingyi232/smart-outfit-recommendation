"""全接口测试脚本"""
import requests
import json

BASE = 'http://127.0.0.1:5000/api'

def test_all():
    print('=== 1. 注册 ===')
    r = requests.post(f'{BASE}/auth/register', json={'username':'testcheck','email':'test@check.com','password':'123456','gender':'male','age':25,'city':'上海','body_type':'normal'})
    print(f'  Register: {r.status_code}')

    print('=== 2. 登录 ===')
    r = requests.post(f'{BASE}/auth/login', json={'username':'zhangsan','password':'123456'})
    d = r.json()
    print(f'  Login: {r.status_code} {d.get("msg","")}')
    token = d['data']['token']
    h = {'Authorization': f'Bearer {token}'}

    print('=== 3. 个人信息 ===')
    r = requests.get(f'{BASE}/auth/profile', headers=h)
    print(f'  GET Profile: {r.status_code}')
    r = requests.put(f'{BASE}/auth/profile', headers=h, json={'nickname':'张三test','city':'广州'})
    print(f'  PUT Profile: {r.status_code} {r.json().get("msg","")}')

    print('=== 4. 天气 ===')
    r = requests.get(f'{BASE}/weather/cities')
    cities = r.json()['data']
    print(f'  Cities: {r.status_code} ({len(cities)} cities)')
    r = requests.get(f'{BASE}/weather/now?city=北京', headers=h)
    w = r.json()['data']
    print(f'  Now: {r.status_code} temp={w["temperature"]} {w["weather_text"]}')
    r = requests.get(f'{BASE}/weather/forecast?city=上海&days=7', headers=h)
    fc = r.json()['data']
    print(f'  Forecast: {r.status_code} ({len(fc)} days)')
    r = requests.get(f'{BASE}/weather/comfort?temp=25&humidity=60&wind=10', headers=h)
    print(f'  Comfort: {r.status_code} {r.json()["data"]}')

    print('=== 5. 推荐 ===')
    r = requests.get(f'{BASE}/recommend/scenes')
    print(f'  Scenes: {r.status_code} {r.json()["data"]}')
    r = requests.get(f'{BASE}/recommend/today?city=北京&scene=通勤', headers=h)
    print(f'  Today: {r.status_code}')
    r = requests.post(f'{BASE}/recommend/generate', headers=h, json={'city':'北京','scene':'运动'})
    print(f'  Generate: {r.status_code}')
    r = requests.get(f'{BASE}/recommend/history?page=1&per_page=5', headers=h)
    hist = r.json()
    print(f'  History: {r.status_code} (total: {hist["data"]["total"]})')

    print('=== 6. 反馈 ===')
    if hist['data']['items']:
        rid = hist['data']['items'][0]['id']
        r = requests.post(f'{BASE}/recommend/feedback', headers=h, json={'recommendation_id': rid, 'rating': 5, 'comment': 'great'})
        print(f'  Feedback: {r.status_code} {r.json().get("msg","")}')

    print('=== 7. 服装 ===')
    r = requests.get(f'{BASE}/clothing/categories')
    print(f'  Categories: {r.status_code} ({len(r.json()["data"])} cats)')
    r = requests.get(f'{BASE}/clothing/list?page=1&per_page=5')
    print(f'  List: {r.status_code} (total: {r.json()["data"]["total"]})')

    print('=== 8. 用户仪表盘 ===')
    r = requests.get(f'{BASE}/user/dashboard', headers=h)
    print(f'  Dashboard: {r.status_code}')
    r = requests.get(f'{BASE}/user/preferences', headers=h)
    print(f'  Preferences: {r.status_code} ({len(r.json()["data"])} prefs)')

    print('=== 9. 管理员 ===')
    r = requests.post(f'{BASE}/auth/login', json={'username':'admin','password':'admin123'})
    at = r.json()['data']['token']
    ah = {'Authorization': f'Bearer {at}'}
    r = requests.get(f'{BASE}/admin/dashboard', headers=ah)
    overview = r.json()['data']['overview']
    print(f'  Dashboard: {r.status_code} users={overview["total_users"]} clothes={overview["total_clothes"]} recs={overview["total_recommendations"]}')
    r = requests.get(f'{BASE}/admin/users?page=1', headers=ah)
    print(f'  Users: {r.status_code} (total: {r.json()["data"]["total"]})')
    r = requests.get(f'{BASE}/admin/clothing?page=1', headers=ah)
    print(f'  Clothing: {r.status_code} (total: {r.json()["data"]["total"]})')
    r = requests.get(f'{BASE}/admin/weather/records?page=1', headers=ah)
    print(f'  Weather: {r.status_code} (total: {r.json()["data"]["total"]})')
    r = requests.get(f'{BASE}/admin/recommendations?page=1', headers=ah)
    print(f'  Recs: {r.status_code} (total: {r.json()["data"]["total"]})')

    print('=== 10. CRUD 服装 ===')
    r = requests.post(f'{BASE}/admin/clothing', headers=ah, json={
        'name':'CRUD测试外套','category_id':4,'description':'测试','warmth_level':3,
        'breathability':3,'waterproof':2,'formality':3,'min_temp':5,'max_temp':25,
        'suitable_scenes':'通勤,旅行','suitable_gender':'all'
    })
    nid = r.json()['data']['id']
    print(f'  ADD: {r.status_code} id={nid}')
    r = requests.put(f'{BASE}/admin/clothing/{nid}', headers=ah, json={'name':'CRUD外套-已修改','warmth_level':4})
    print(f'  UPDATE: {r.status_code} {r.json().get("msg","")}')
    r = requests.delete(f'{BASE}/admin/clothing/{nid}', headers=ah)
    print(f'  DELETE: {r.status_code} {r.json().get("msg","")}')

    print('=== 11. 用户启禁 ===')
    users = requests.get(f'{BASE}/admin/users?page=1&per_page=20', headers=ah).json()['data']['items']
    tu = [u for u in users if u['username'] == 'testcheck']
    if tu:
        r = requests.put(f'{BASE}/admin/users/{tu[0]["id"]}/toggle', headers=ah)
        print(f'  Toggle: {r.status_code} {r.json().get("msg","")}')

    print('\n=== ALL TESTS PASSED ===')

if __name__ == '__main__':
    test_all()
