## Deploying the USKPA Website
[:arrow_left: Back to USKPA
Documentation](../docs)

All instances are hosted by [Heroku].

* Development - https://uskpa-dev.herokuapp.com/
* Production - https://uskpa-prod.herokuapp.com/

### Heroku

We use the [Heroku CLI], Heroku dashboard, and Heroku Github
Integration to manage instances and automate releases.

Currently, the [master] branch is deployed to the `Development` environment
on each commit for which the unit test suite executes without error.

Please see the Heroku CLI docs on [deploying with git](https://devcenter.heroku.com/articles/git).

**Note:** Interacting with the specific Heroku Applications
discussed below is limited to those with the necessary permissions.

### Development
*Heroku app: uskpa-dev*

Deployed automatically via Heroku Github integration from the [master] branch.

The staging environment exists to test new releases prior
to their production deployment.

The staging database and application are independent of
and share no data with the production instance.

Example of a manual deploy using the [Heroku CLI]:

```shell
$ heroku login
$ heroku git:remote -a uskpa-dev
$ git push heroku master

# If migrations are required
$ heroku run python manage.py migrate
```

### Production
*Heroku app: uskpa-prod*

Deployed manually from: Github [master] branch

Application for the the production USKPA website.

See [deploying changes](./change-workflow.md#deploying-changes) for details on making changes to the production instance.

### Initial Data

The USKPA system depends on several models being populated
to enable a complete environment for both users and administrators.

To load this initial data upon release to a new environment we
use functionality provided by Django.

Additional data will be included as development continues.

```shell
$ heroku run python manage.py loaddata initial-data.json
```

### Environment Variables

We leverage Heroku Config variables for instance configuration.

The following variables can be set in Heroku to alter the site's behavior.

Var | Value | Destination
--- | --- | ---
ADMINS | Comma delimited list of email addresses | ``settings.ADMINS``
DEBUG | TRUE/FALSE | ``settings.DEBUG``should only be set to `TRUE` for development environments
DJANGO_LOG_LEVEL | INFO, DEBUG, or ERROR | Controls logging level of Django process, defaults to ERROR in production
CONTACT_US | email address | Email address used for all `contact-us` links through site, also used as default value for DJANGO_FROM_EMAIL
STAGE | live | Set value to 'live' for production instance to toggle deployed instance status banner displayed at the top of each template.
DJANGO_ALLOWED_HOSTS | Comma delimited list of allowed hosts for django application | ``settings.ALLOWED_HOSTS``

### Email - One time Setup

Additional steps are required to enable outgoing email functionality from a new Heroku instance.

Please see the [Email documentation](email.md) for detailed instructions.

[Heroku]: https://heroku.com
[Heroku CLI]: https://devcenter.heroku.com/articles/heroku-cli
[master]: https://github.com/18F/uskpa/tree/master
