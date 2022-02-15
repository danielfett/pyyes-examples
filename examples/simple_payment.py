import yes
import cherrypy
import json
from pathlib import Path
import sys
import yaml

yes_configuration = yes.YesConfiguration.sandbox_test_from_env()

if len(sys.argv) > 1:
    with open(sys.argv[1], 'r') as f:
        yes_configuration = yaml.load(f.read())

claims = {
    "id_token": {
        "verified_claims": {
            "claims": {"given_name": None,},
            "verification": {"trust_framework": None},
        }
    },
    "userinfo": {
        "verified_claims": {
            "claims": {"family_name": None,},
            "verification": {"trust_framework": None},
        }
    },
}


class YesExample:
    @cherrypy.expose
    def start(
        self, amount, remittance_information, creditor_name, creditor_account_iban
    ):
        """
        Starting the yes® flow after the user clicked on the yes® button.
        """
        yessession = yes.YesPaymentSession(
            amount, remittance_information, creditor_name, creditor_account_iban
        )
        cherrypy.session["yes"] = yessession
        yesflow = yes.YesPaymentFlow(yes_configuration, cherrypy.session["yes"])
        ac_redirect = yesflow.start_yes_flow()

        cherrypy.log(f"Account chooser redirection to {ac_redirect}.")
        raise cherrypy.HTTPRedirect(ac_redirect)

    @cherrypy.expose
    def accb(self, state, issuer_url=None, error=None, selected_bic=None):
        """
        Account chooser callback. The user arrives here after selecting a bank.

        Note that the URL of this endpoint has to be registered with yes for
        your client. 
        """
        yesflow = yes.YesPaymentFlow(yes_configuration, cherrypy.session["yes"])

        try:
            authorization_endpoint_uri = yesflow.handle_ac_callback(
                state, issuer_url, error
            )
        except yes.YesUserCanceledError:
            cherrypy.HTTPRedirect("/")
        except yes.YesError as exception:
            # not implemented here: show nice error messages
            raise cherrypy.HTTPError(400, str(exception))

        raise cherrypy.HTTPRedirect(authorization_endpoint_uri)

    @cherrypy.expose
    def oidccb(self, iss, code=None, error=None, error_description=None):
        """
        OpenID Connect callback endpoint. The user arrives here after going
        through the authentication/authorizaton steps at the bank.

        Note that the URL of this endpoint has to be registered with yes for
        your client. 
        """
        yesflow = yes.YesPaymentFlow(yes_configuration, cherrypy.session["yes"])

        try:
            yesflow.handle_oidc_callback(iss, code, error, error_description)
        except yes.YesAccountSelectionRequested as exception:
            # user selected "select another bank" → must send user back to account chooser
            raise cherrypy.HTTPRedirect(exception.redirect_uri)
        except yes.YesError as exception:
            # not implemented here: show nice error messages
            raise cherrypy.HTTPError(400, str(exception))

        # id token and userinfo are alternative ways to retrieve user information - see developer guide
        user_data_id_token = yesflow.send_token_request()
        user_data_userinfo = yesflow.send_userinfo_request()

        return (
            "Got user data in the ID token: <pre>"
            + json.dumps(user_data_id_token, indent=4)
            + "</pre> ... and from the userinfo endpoint: <pre>"
            + json.dumps(user_data_userinfo, indent=4)
            + "</pre>"
        )


class Root:
    @cherrypy.expose
    def default(self):
        return ""


PATH = Path(__file__).parent.parent.resolve() / "static"

cherrpy_config = {
    "global": {"server.socket_port": 3000},
    "/": {
        "tools.sessions.on": "True",
        "tools.staticdir.on": True,
        "tools.staticdir.dir": PATH,
        "tools.staticdir.index": "payment.html",
        "log.access_file": "access.log",
        "log.error_file": "error.log",
    },
}
cherrypy.tree.mount(Root(), "/", cherrpy_config)
cherrypy.quickstart(YesExample(), "/yes", cherrpy_config)

