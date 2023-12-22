from django import forms
from .models import Comment, Listing

# Here we have created a form for creating a new listing.
class ListingForm(forms.ModelForm): # ModelForm is a class that allows to create a form based on a model.
    class Meta: 
        model = Listing
        fields = ['title', 'description', 'starting_bid', 'image_url', 'category']

# Here we have created a form for creating a new comment.
class CommentForm(forms.ModelForm): # ModelForm is a class that allows to create a form based on a model.
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': "Your Comment"
        }