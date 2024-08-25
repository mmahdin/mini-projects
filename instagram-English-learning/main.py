import instaloader

# Define your proxy
proxy = "http://26.26.26.1:8080"
# proxy = "http://127.0.0.1:2080"

# Initialize Instaloader with proxy
L = instaloader.Instaloader()

# Configure the session to use the proxy
L.context._session.proxies = {
    'http': proxy,
    'https': proxy,
}

# Define the profile to download
profile_name = 'words.2u'

# Create a resume prefix (you can change this to a different name if you want)
resume_prefix = f'{profile_name}_resume'

# Try to resume the download
L.resume_prefix = resume_prefix

# Fetch the profile
profile = instaloader.Profile.from_username(L.context, profile_name)

# Iterate over the posts in the profile and download them
with open('cnt', 'r') as file:
    cnt = int(file.readline())

for post in profile.get_posts():
    with open('cnt', 'w') as file:
        file.write(str(cnt))
    print(cnt)
    print(f"Post URL: https://www.instagram.com/p/{post.shortcode}/")
    print("-" * 80)

    # Download the post
    L.download_post(post, target=profile.username)
    cnt += 1

print("Download completed.")
