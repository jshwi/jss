<!--
This file is auto-generated and any changes made to it will be overwritten
-->
# tests

## tests._test


### 404 error

Test `404 Not Found` is returned when a route does not exist.


### Admin access control

Test access to admin console restricted to admin user.


### Admin access without login

Asserts that the `AnonymousUserMixin` error will not be raised.

This commit fixes the following error causing app to crash if user
is not logged in:

> AttributeError:
> ‘AnonymousUserMixin’ object has no attribute ‘admin’


### Admin page

Test rendering of admin page.


### Admin required

Test requirement that admin user be logged in to post.

An admin user must be logged in to access the CREATE, “update”,
and “delete” views.

The logged-in user must be the author of the post to access the
update and delete views, otherwise a `403 Forbidden` status is
returned.


### All routes covered

Test all routes that need to be tested will be.


### Author required

Test author’s name when required.

The create and update views should render and return a `200 OK`
status for a `GET` request.

When valid data is sent in a `POST` request the create view should
insert the new post data into the database and the update view
should modify the existing data. Both pages should show an error
message on invalid data.


### Avatar

Test generated avatar URL for expected value.


### Bad token

Test user denied when jwt for resetting password is expired.


### Book call

Test booking of call.


### Config copyright

Test parsing of metadata from project root.


### Confirmation email confirmed

Test user redirected when already confirmed.


### Confirmation email resend

Test user receives email when requesting resend.


### Confirmation email unconfirmed

Test user is moved from confirmed as False to True.


### Create

Test create view functionality.

When valid data is sent in a `POST` request the create view should
insert the new post data into the database.


### Create admin

Test commands called when invoking `flask create admin`.


### Create command

Test cli.


### Create user email exists

Test creation of a new user whose email is already registered.


### Create user exists

Test creation of a new user that exists.


### Create user no exist

Test creation of a new user that doesn’t exist.


### Create user passwords no match

Test creation of a new user where passwords don’t match.


### Csp class

Test the `ContentSecurityPolicy` object.

Test the assigning of a default policy, and the addition of any
custom configured policy items.


### Csp report

Test response for CSP violations route.


### Delete

Test deletion of posts.

The “delete” view should redirect to the index URl and the post
should no longer exist in the database.


### Edit profile

Test edit profile page.


### Email does not exist

Test user notified when email does not exist for password reset.


### Exists required

Test `404 Not Found` is returned when a route does not exist.


### Export

Test export to 

```
dict_
```

 function for models.


### Follow

Test functionality of user follows.


### Follow posts

Test functionality of post follows.


### Get smtp handler

Test correct values passed to `SMTPHandler`.


### Has languages

Test languages collected for config property.


### Headers

Assert headers are secure.


### Index

Test login and subsequent requests from the client.

The index view should display information about the post that was
added with the test data. When logged in as the author there should
be a link to edit the post.

We can also test some more authentication behaviour while testing
the index view. When not logged in each page shows links to log in
or register. When logged in there’s a link to log out.


### Inspect profile no user

Assert that unhandled error is not raised for user routes.

This commit fixes the following error:

> AttributeError: ‘NoneType’ object has no attribute ‘posts’

If a non-existing user is searched, prior to this commit, the route
will use methods belonging to the user (assigned None).

Prefer to handle the exception and return a `404: Not Found` error
instead.

e.g.  Use `User.query.filter_by(username=username).first_or_404()`
instead of `User.query.filter_by(username=username).first()`


### Jinja2 required extensions

Test `jinja2.ext` has attrs needed for language support.


### Login

Test login functionality.


### Login confirmed

Test login functionality once user is verified.


### Login required

Test requirement that user be logged in to post.

A user must be logged in to access the CREATE, “update”, and
“delete” views.

The logged-in user must be the author of the post to access the
update and delete views, otherwise a `403 Forbidden` status is
returned.


### Login validate

Test incorrect username and password error messages.


### Logout

Test logout functionality.


### Navbar home config switch

Test that the navbar Home link appropriately switches on and off.


### Navbar user dropdown config switch

Test that the user dropdown appropriately switches on and off.


### Order cancel

Test order cancellation view.


### Order success

Test order success view.


### Pagination nav

Test links are rendered when more than one page exists.


### Post follow unfollow routes

Test `POST` request to follow and unfollow a user.


### Post page

Test for correct contents in post page response.


### Profile page

Test response when visiting profile page of existing user.


### Redundant token

Test user notified that them being logged in has voided token.


### Register

The register view should render successfully on `GET`.

On `POST`, with valid form data, it should redirect to the login
URL and the user’s data should be in the database. Invalid data
should display error messages.

To test that the page renders successfully a simple request is made
and checked for a `200 OK` `status_code`.

Headers will have a `Location` object with the login URL when the
register view redirects to the login view.


### Register invalid fields

Test different invalid input and error messages.


### Request password reset email

Test that the correct email is sent to user for password reset.


### Reserved usernames

Test that reserved names behave as taken names would in register.


### Reset password

Test the password reset process.


### Send message

Test sending of personal messages from one user to another.


### Static route default

Specifically test all status codes of routes.


### Translate args

Test commands called when invoking `flask translate init`.


### Translate compile

Test commands called when invoking `flask translate compile`.


### Translate init files

Test management of files when running `flask translate init`.


### Translate update args

Test commands called when invoking `flask translate update`.


### Translate update files

Test management of files when running `flask translate update`.


### Unconfirmed

Test when unconfirmed user tries to enter restricted view.


### Update

Test update view modifies the existing data.


### Upload bad file

Test uploading of an invalid file.


### Upload good file

Test uploading of a valid file.


### Upload unknown file type

Test uploading of file that’s invalid as it can’t be determined.


### Upload view

Test upload create view.


### User name change accessible

Test that even after name-change user is accessible by old name.

Only valid if the old name has not already been adopted by someone
else.


### Version dropdown

Test version dropdown.

Test all 3 variations of unordered list items.


### Versioning handle index error

Test versioning route when passing to large a revision to update.


### Versions

Test versioning of posts route.


### Versions update

Test versioning of posts route when passing revision to update.


