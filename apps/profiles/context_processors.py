
def profile_picture(request):
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        photo = request.user.profile.photo
        return {
            'profile_picture': photo.url if photo else "https://static.vecteezy.com/system/resources/previews/009/292/244/non_2x/default-avatar-icon-of-social-media-user-vector.jpg"
        }

    return {
        'profile_picture': "https://static.vecteezy.com/system/resources/previews/009/292/244/non_2x/default-avatar-icon-of-social-media-user-vector.jpg"
    }
