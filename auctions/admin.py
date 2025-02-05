from django.contrib import admin
from .models import User, Listing, Comment, Bid, Category

# Register your models here.

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'starting_bid', 'current_bid', 'user', 'active', 'category')
    search_fields = ('title', 'description', 'user__username')
    list_filter = ('active', 'category')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('comment_text', 'user', 'listing')
    search_fields = ('comment_text', 'user__username', 'listing__title')
    list_filter = ('listing', 'user')

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('user', 'bid_amount', 'listing')
    search_fields = ('user__username', 'listing__title')
    list_filter = ('listing', 'user')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
