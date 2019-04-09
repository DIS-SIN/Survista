import os
from src import create_app
import warnings
# when using the flask cli the environment is set through this variable
mode = os.environ.get("FLASK_ENV")

# if the variable is not set or not a correct environment
# the environment should default to production
if mode is None or mode != "production" and mode != "development":
    mode = "production"
    warnings.warn(
        "FLASK_ENV was not set or value was not one of " +
        "production or development. Defaulting to production")

application = create_app(mode,
                         static_path=os.path.abspath('./static'),
                         templates_path=os.path.abspath('./templates'),
                         instance_path=os.path.abspath('./instance'))

if __name__ == "__main__":
    application.run()
