# Examples for pyyes

This repository contains examples for the usage of the pyyes yes® library.

> :warning: **Please read the [license](LICENSE) before using!** This is not an SDK for yes and not part of any contract you might have with yes.com.


## Setup
```
git clone https://github.com/yescom/pyyes-examples.git
pip3 install -r requirements.txt
```

## Running the Examples

**Step 1:** Acquire credentials to access the yes® ecosystem as described [here](https://www.yes.com/docs/rp-devguide/latest/ONBOARDING/index.html). Note that for testing **the identity flow**, you can use the Sandbox Demo Client credentials published [here](https://www.yes.com/docs/rp-devguide/latest/ONBOARDING/index.html#_sandbox_demo_client).

**Step 2:** Make the credentials available in environment variables:

```bash
export YES_SANDBOX_TEST_CERT=/home/user/yes-client/cert.pem
export YES_SANDBOX_TEST_KEY=/home/user/yes-client/key.pem  
export YES_SANDBOX_TEST_CLIENT_ID=sandbox.yes.com:e85ff3bc-96f8-4ae7-b6b1-894d8dde9ebe
export YES_SANDBOX_TEST_REDIRECT_URI=http://localhost:3000/yes/oidccb
```

**Step 3:** Now run the example:

```bash
python3 examples/simple_identity.py
```
or
```bash
python3 examples/full_signing_flow.py
```

Point your browser to http://localhost:3000/ to start the example.
