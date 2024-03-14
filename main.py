import asyncio
import httpx


USERNAME = "YOUR_USERNAME"
EMAIL = "YOUR_EMAIL"
PASSWORD = "YOUR_PASSWORD"

async def main():
    login_url = "https://www.clickasnap.com/api/login"
    feed_url = "https://www.clickasnap.com/api/photos/feed"
    likes_url_template = "https://www.clickasnap.com/api/photos/{userId}/photo/{id}/like"
    
    payload = {
        "username": USERNAME,
        "email": EMAIL,
        "password": PASSWORD
    }

    async with httpx.AsyncClient() as client:
        login_response = await client.post(login_url, json=payload)

        if login_response.status_code == 200:
            print("Login successful.")

            cookies = login_response.cookies
            headers = {
                "Cookie": "; ".join(f"{name}={value}" for name, value in cookies.items()), 
                "Sec-Fetch-Site": "same-origin",
                "Origin": "https://www.clickasnap.com",
                "Content-Type": "application/json"
            }

            params = {
                "from": 0,
                "size": 40,
                "sort[createdAt]": "desc",
                "collapse": "groupId",
                "query[userRole][0]": "Plan_PRO_Yearly",
                "query[userRole][1]": "Plan_PRO_Monthly",
                "query[userRole][2]": "Plan_SELLER_Yearly",
                "query[userRole][3]": "Plan_SELLER_Monthly",
                "query[userRole][4]": "Plan_UPLOAD+_Yearly",
                "query[userRole][5]": "Plan_UPLOAD+_Monthly"
            }

            while True:
                feed_response = await client.get(feed_url, headers=headers, params=params)
                print(feed_response)
                if feed_response.status_code == 200:
                    feed_data = feed_response.json()
                    items = feed_data.get("items", [])

                    print(items)

                    if not items:
                        break  # No more items, exit loop

                    for item in items:
                        user_id = item["userId"]
                        photo_id = item["id"]
                        likes_url = likes_url_template.format(userId=user_id, id=photo_id)

                        headers = {
                            "Cookie": "; ".join(f"{name}={value}" for name, value in cookies.items()), 
                            "Sec-Fetch-Site": "same-origin",
                            "Origin": "https://www.clickasnap.com",
                            "Content-Type": "application/json",
                            "Accept": "application/json",
                            "Accept-Encoding": "gzip, deflate, br",
                            "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7,ru;q=0.6",
                            "Content-Length": "0",
                            "Sec-Ch-Ua": "\"Chromium\";v=\"116\", \"Not)A;Brand\";v=\"24\", \"Google Chrome\";v=\"116\"",
                            "Sec-Ch-Ua-Mobile": "?0",
                            "Sec-Ch-Ua-Platform": "\"macOS\"",
                            "Sec-Fetch-Dest": "empty",
                            "Sec-Fetch-Mode": "cors",
                            "Sec-Fetch-Site": "same-origin",
                            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
                        }

                        has_like = await client.get(likes_url + "s", headers=headers)
                        if has_like.json()["hasUserLiked"] == "true":
                            print(likes_url + "s already has like")
                            continue

                        likes_response = await client.post(likes_url, headers=headers)
                        if likes_response.status_code == 200:
                            likes_data = likes_response.json()
                            print("Likes for user", user_id, "and photo", photo_id, ":", likes_response.status_code)
                        else:
                            print("Failed to fetch likes data with status code:", likes_response.status_code)
                        
                        # Update from parameter for the next batch of items
                        params["from"] += 1
                    else:
                        break

        else:
            print("Login failed with status code:", login_response.status_code)

asyncio.run(main())
