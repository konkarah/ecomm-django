# ==================== MODELS FOR EXAMPLES ====================
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, F, Count, Avg, Sum, Max, Min, Prefetch

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    birth_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)

class Post(models.Model):
    title = models.CharField(max_length=200, db_index=True)
    content = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    categories = models.ManyToManyField(Category, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    published = models.BooleanField(default=False, db_index=True)
    view_count = models.IntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=['published', '-created_at']),
            models.Index(fields=['author', 'created_at']),
        ]

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

# ==================== 1. COMPLEX JOINS & AGGREGATIONS ====================

# Problem: Get authors with their post count, average views, and latest post date
def get_author_statistics():
    """
    SQL equivalent:
    SELECT a.*, COUNT(p.id) as post_count, AVG(p.view_count), MAX(p.created_at)
    FROM author a 
    LEFT JOIN post p ON a.id = p.author_id AND p.published = true
    GROUP BY a.id
    """
    return Author.objects.select_related('user').annotate(
        post_count=Count('posts', filter=Q(posts__published=True)),
        avg_views=Avg('posts__view_count', filter=Q(posts__published=True)),
        latest_post_date=Max('posts__created_at', filter=Q(posts__published=True)),
        total_views=Sum('posts__view_count')
    ).order_by('-post_count')

# Problem: Get posts with comment count and latest comment date
def get_posts_with_comment_stats():
    """Complex aggregation with filtering"""
    return Post.objects.select_related('author__user').annotate(
        comment_count=Count('comments', filter=Q(comments__approved=True)),
        latest_comment=Max('comments__created_at', filter=Q(comments__approved=True)),
        reply_count=Count('comments__replies', filter=Q(comments__replies__approved=True))
    ).filter(published=True).order_by('-latest_comment')

# Problem: Complex filtering with multiple conditions
def get_popular_posts_by_category(category_name, min_views=100):
    """Find popular posts in a specific category"""
    return Post.objects.filter(
        Q(categories__name__icontains=category_name) &
        Q(view_count__gte=min_views) &
        Q(published=True) &
        (Q(author__user__is_active=True) | Q(author__user__is_staff=True))
    ).select_related('author__user').prefetch_related('categories').distinct()

# ==================== 2. SUBQUERIES ====================

# Problem: Get authors who have more posts than the average
def get_prolific_authors():
    """Using subqueries to compare against averages"""
    from django.db.models import Subquery, OuterRef
    
    # Subquery to calculate average posts per author
    avg_posts = Author.objects.aggregate(
        avg_count=Avg('posts__id')
    )['avg_count'] or 0
    
    return Author.objects.annotate(
        post_count=Count('posts')
    ).filter(post_count__gt=avg_posts)

# Problem: Get posts with their author's total post count
def get_posts_with_author_post_count():
    """Subquery to get related aggregated data"""
    from django.db.models import Subquery, OuterRef
    
    # Subquery to get author's total post count
    author_post_count = Post.objects.filter(
        author=OuterRef('author')
    ).aggregate(total=Count('id'))['total']
    
    return Post.objects.select_related('author').annotate(
        author_total_posts=Subquery(
            Author.objects.filter(
                id=OuterRef('author_id')
            ).annotate(
                total_posts=Count('posts')
            ).values('total_posts')
        )
    )

# Problem: Get latest comment for each post (window functions alternative)
def get_posts_with_latest_comments():
    """Using subqueries for latest related objects"""
    from django.db.models import Subquery, OuterRef
    
    latest_comments = Comment.objects.filter(
        post=OuterRef('pk'),
        approved=True
    ).order_by('-created_at')
    
    return Post.objects.annotate(
        latest_comment_content=Subquery(latest_comments.values('content')[:1]),
        latest_comment_author=Subquery(latest_comments.values('author__username')[:1]),
        latest_comment_date=Subquery(latest_comments.values('created_at')[:1])
    )

# ==================== 3. N+1 PROBLEM SOLUTIONS ====================

# BAD: N+1 Problem
def get_posts_bad():
    """This will cause N+1 queries"""
    posts = Post.objects.all()  # 1 query
    for post in posts:
        print(post.author.user.username)  # N queries (one per post)
        print(post.categories.count())     # N more queries

# GOOD: Optimized with select_related and prefetch_related
def get_posts_optimized():
    """Optimized version - only 3 queries total"""
    posts = Post.objects.select_related(
        'author__user'  # JOIN author and user tables
    ).prefetch_related(
        'categories'    # Separate optimized query for many-to-many
    )
    
    for post in posts:
        print(post.author.user.username)  # No additional query
        print(post.categories.count())     # No additional query

# Advanced: Custom Prefetch with filtering
def get_posts_with_approved_comments():
    """Only prefetch approved comments"""
    approved_comments = Prefetch(
        'comments',
        queryset=Comment.objects.filter(approved=True).select_related('author'),
        to_attr='approved_comments'
    )
    
    return Post.objects.prefetch_related(approved_comments)

# Complex optimization: Nested prefetching
def get_categories_with_posts_and_authors():
    """Prefetch categories -> posts -> authors in one go"""
    return Category.objects.prefetch_related(
        Prefetch(
            'posts',
            queryset=Post.objects.filter(published=True).select_related('author__user'),
            to_attr='published_posts'
        )
    )

# ==================== 4. CUSTOM MANAGERS & QUERYSETS ====================

class PublishedPostQuerySet(models.QuerySet):
    """Custom QuerySet with reusable methods"""
    
    def published(self):
        return self.filter(published=True)
    
    def by_author(self, author):
        return self.filter(author=author)
    
    def popular(self, min_views=100):
        return self.filter(view_count__gte=min_views)
    
    def recent(self, days=7):
        from django.utils import timezone
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff)
    
    def with_stats(self):
        """Add comment and view statistics"""
        return self.annotate(
            comment_count=Count('comments'),
            avg_comment_length=Avg('comments__content__length')
        )
    
    def search(self, query):
        """Full-text search across title and content"""
        return self.filter(
            Q(title__icontains=query) | Q(content__icontains=query)
        )

class PostManager(models.Manager):
    """Custom manager with business logic"""
    
    def get_queryset(self):
        return PublishedPostQuerySet(self.model, using=self._db)
    
    def published(self):
        return self.get_queryset().published()
    
    def popular_recent(self, days=7, min_views=50):
        """Get popular posts from recent days"""
        return self.get_queryset().recent(days).popular(min_views)

# Add to Post model:
# objects = PostManager()

# Usage examples:
def example_custom_manager_usage():
    # Chain custom methods
    popular_posts = Post.objects.published().popular().recent().with_stats()
    
    # Search with optimization
    search_results = Post.objects.published().search('django').select_related('author')
    
    # Business logic methods
    trending = Post.objects.popular_recent(days=3, min_views=100)

# ==================== 5. ADVANCED QUERY TECHNIQUES ====================

# F expressions for database-level operations
def increment_view_counts(post_ids):
    """Increment view count at database level"""
    Post.objects.filter(id__in=post_ids).update(
        view_count=F('view_count') + 1
    )

# Conditional aggregations
def get_post_engagement_stats():
    """Complex conditional aggregations"""
    from django.db.models import Case, When, IntegerField
    
    return Post.objects.aggregate(
        high_engagement=Count(
            Case(When(view_count__gte=1000, then=1), output_field=IntegerField())
        ),
        medium_engagement=Count(
            Case(When(view_count__range=(100, 999), then=1), output_field=IntegerField())
        ),
        low_engagement=Count(
            Case(When(view_count__lt=100, then=1), output_field=IntegerField())
        )
    )

# Raw SQL for complex queries
def get_monthly_post_stats():
    """When ORM becomes too complex, use raw SQL"""
    from django.db import connection
    
    query = """
    SELECT 
        EXTRACT(YEAR FROM created_at) as year,
        EXTRACT(MONTH FROM created_at) as month,
        COUNT(*) as post_count,
        AVG(view_count) as avg_views
    FROM blog_post 
    WHERE published = true
    GROUP BY EXTRACT(YEAR FROM created_at), EXTRACT(MONTH FROM created_at)
    ORDER BY year DESC, month DESC
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()

# ==================== 6. QUERY OPTIMIZATION TECHNIQUES ====================

def optimized_post_list_view():
    """Production-ready optimized query"""
    return Post.objects.select_related(
        'author__user'  # Avoid N+1 for author data
    ).prefetch_related(
        Prefetch(
            'categories',
            queryset=Category.objects.only('name'),  # Only fetch name field
            to_attr='category_list'
        ),
        Prefetch(
            'comments',
            queryset=Comment.objects.filter(approved=True).select_related('author')[:5],
            to_attr='recent_comments'
        )
    ).annotate(
        comment_count=Count('comments', filter=Q(comments__approved=True))
    ).only(  # Only fetch needed fields
        'title', 'created_at', 'view_count', 'author__user__username'
    ).filter(published=True)

# Database query analysis
def analyze_query_performance():
    """How to debug query performance"""
    from django.db import connection
    from django.conf import settings
    
    # Enable query logging in settings
    settings.LOGGING['loggers']['django.db.backends'] = {
        'level': 'DEBUG',
        'handlers': ['console']
    }
    
    # Reset query log
    connection.queries_log.clear()
    
    # Execute your query
    list(Post.objects.published().with_stats())
    
    # Analyze queries
    print(f"Number of queries: {len(connection.queries)}")
    for query in connection.queries:
        print(f"Time: {query['time']}, SQL: {query['sql']}")

# ==================== 7. COMMON ASSESSMENT QUESTIONS ====================

"""
1. "Fix this N+1 query problem"
   - Look for loops accessing related objects
   - Use select_related for ForeignKey/OneToOne
   - Use prefetch_related for ManyToMany/reverse FK

2. "Optimize this slow query"
   - Add database indexes
   - Use only() to limit fields
   - Add select_related/prefetch_related
   - Consider query splitting

3. "Write a query to find..."
   - Use Q objects for complex conditions
   - Annotations for calculated fields
   - Subqueries for comparing against aggregates

4. "How would you implement full-text search?"
   - PostgreSQL: Use search vectors
   - MySQL: Use FULLTEXT indexes
   - Generic: Use icontains with indexes

5. "Design a query for reporting dashboard"
   - Use aggregations and annotations
   - Consider raw SQL for complex reports
   - Think about caching strategy
"""