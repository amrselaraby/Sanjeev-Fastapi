from fastapi import status, Depends, Response, HTTPException, APIRouter
from sqlalchemy import func

from app import oauth2
from .. import models, schemas, oauth2
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List, Optional

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=List[schemas.PostOut])
def get_posts(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: Optional[str] = "",
):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    queryset = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(
            models.Vote,
            models.Vote.post_id == models.Post.id,
            isouter=True,
        )
        .group_by(models.Post.id)
    )

    posts = (
        queryset.filter(models.Post.title.contains(search))
        .offset(skip)
        .limit(limit=limit)
        .all()
    )
    return posts


@router.post("/", response_model=schemas.Post)
def create_post(
    post: schemas.CreatePost,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    # cursor.execute(
    #     """INSERT INTO posts (title,content,published) VALUES (%s,%s,%s) RETURNING *""",
    #     (post.title, post.content, post.published),
    # )
    # new_post = cursor.fetchone()
    # conn.commit()

    new_post = models.Post(
        owner_id=current_user.id,
        **post.dict(),
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))
    # post = cursor.fetchone()
    queryset = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(
            models.Vote,
            models.Vote.post_id == models.Post.id,
            isouter=True,
        )
        .group_by(models.Post.id)
    )
    post = queryset.filter(models.Post.id == id).first()
    if post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The post you are trying to search for does not exist, please use another id",
        )
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING *""", (str(id),))
    # delete_post = cursor.fetchone()
    # conn.commit()
    queryset = db.query(models.Post).filter(models.Post.id == id)
    post = queryset.first()
    if post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The post you are trying to delete does not exist, please use another id",
        )
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission",
        )
    queryset.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)
def update_post(
    id: int,
    update_post: schemas.CreatePost,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    # cursor.execute(
    #     """UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *""",
    #     (post.title, post.content, post.published, str(id)),
    # )
    # updated_post = cursor.fetchone()
    # conn.commit()
    queryset = db.query(models.Post).filter(models.Post.id == id)
    post = queryset.first()

    if post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The post you are trying to update does not exist, please use another id",
        )
    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission",
        )

    queryset.update(update_post.dict(), synchronize_session=False)
    db.commit()
    return queryset.first()
