import ray
from ray import serve

ray.init()
serve.start()

@serve.deployment
class Preprocessor:

    def __init__(self, split, A_name, B_name):
        self.split = split
        self.A_handle = serve.get_deployment(A_name).get_handle(sync=False)
        self.B_handle = serve.get_deployment(B_name).get_handle(sync=False)
    
    async def __call__(self, request):
        self.some_function(request)

        # Pass request to a downstream model based on contents
        if request < self.split:
            return self.A_handle(request)
        else:
            return self.B_handle(request)
    
    # See https://docs.ray.io/en/master/serve/core-apis.html?highlight=reconfigure#user-configuration-experimental
    def reconfigure(self, config):
        self.split = config["split"]

    def some_function(self, request):
        # This function does some preprocessing to a request
        pass


@serve.deployment
class Model:

    def __init__(self, model_path: str):
        self.model = self.load_model(model_path)
    
    async def __call__(self, request):
        return self.model.call(request)
    
    # See https://docs.ray.io/en/master/serve/core-apis.html?highlight=reconfigure#user-configuration-experimental
    def reconfigure(self, config):
        self.model = self.load_model(config["model_path"])
    
    def load_model(self, model_path: str):
        # This function loads a model from the model_path
        pass

Model.options(name="model_A").deploy("./model_A.pkl")
Model.options(name="model_B").deploy("./model_B.pkl")
Preprocessor.deploy(0.7, "model_A", "model_B")
