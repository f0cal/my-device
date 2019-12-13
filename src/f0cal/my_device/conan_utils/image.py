class Image:

    @classmethod
    def from_yaml(cls, yaml_path):
        pass

    def install(self, **kwargs):
        cmd = ["salt-call", "--local", "state.sls", "f0cal.my-device.image.install"]
        return self._saltbox_run(cmd, pillar=self.pillar_json, saltenv="f0cal-public")

    def test(self, **kwargs):
        pass

    def _import(self, **kwargs):
        pass

    def overlay(self, **kwargs):
        cmd = ["salt-run", "state.orchestrate", "f0cal."]
        return self._saltbox_run(cmd, pillar=self.pillar_json, saltenv="f0cal-private")

    @classmethod
    def _saltbox_run(cls, cmd, pillar, saltenv=None, **kwargs):
        config = saltbox.SaltBoxConfig.from_env()
        with saltbox.SaltBox.executor_factory(config) as api:
            api.execute(cmd)