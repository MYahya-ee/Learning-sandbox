from fastapi import FastAPI
app  = FastAPI()

posts = {1: {"header": "Post 1", "content": "This is first post."},
         2: {"header": "Post 2", "content": "This is second post."},
         3: {"header": "Post 3", "content": "This is third post."}
         }
@app.get("/posts")
def fetch_all_posts(limit: int = None):
    if limit:
        return list(posts.values())[:limit]
    else:
        return posts 

@app.get("/posts/{id}")
def fetch_postby_id(id : int):
    if id in posts:
        return posts[id]
    else:
        return {"message": "Post not found."}