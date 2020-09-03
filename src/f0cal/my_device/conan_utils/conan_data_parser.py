import yaml


# TODO USE A PROPER JSON/YAML SCHEMA HERE
class ConanDataValidator:
    @classmethod
    def validate(cls, conandata, expected_keys):
        conandata_keys = set(conandata.keys())
        if not conandata_keys.issuperset(expected_keys):
            raise Exception(
                f'The following required keys are missing from conandata.yml:\n {expected_keys.difference(conandata_keys)}')
        return True
