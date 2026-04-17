# Context

Recently, i've been programming a simple cloud webserver in Go.

And of course, it is unavoidable when including accounts, how to make sure a user is who he pretends to be when he connects to a page.

Of course, there are authetication and session cookies, but in this blog we like to imagine another way to achive this.

**So let's implement a custom authentication mechanism that does not rely on cookies at all. Sounds cool.**

The projetc is available on this website [Friendly\_Cloud](../static/files/Friendly_Clound.zip)

Or here on GitHub [repo](https://github.com/julienlargetpiet/Friendly_Cloud)

# Method

The `credentials` database consists of 3 columns:

- `username`
- `password`
- `temp_password`

The `password` is only used in the login process, to verify that the users gives the right password.

After validation, a randomly temporary password is generated, stored in the third column, and passed in the URL with the username.

When the client connects to the next page, the server extracts the `username` and the `temp_password` from the URL, and evaluates them in the database, if the temporary password is valid with the given username, a new random and temporary password is generated then stored in the third columnn for the current username, and passed as an extension of the URLs the user might click on for the next page.

With this method, we assume that the body is encrypted (default with https), because even if the URL is not encrypted, or if somebody next to you tries to copy the same URL your browser is showing to hijack you from your account, this URL is no more valid!

This is what i call a **rotation link mechanism**.

# Limitations

If using a `SQL` like database, the server will call a lot of `UPDATE credentials SET temp_password='newone';` which can be a lot of work compared to extracting content of cookies.