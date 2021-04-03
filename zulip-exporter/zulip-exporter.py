import zulip
import json
import logging
from os import environ
from sys import exit
from time import sleep
from prometheus_client import start_http_server, REGISTRY
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily


httpport = environ.get('HPORT', 9863)
frequency = environ.get('SLEEP', 120)
client = zulip.Client()

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

class InfoCollector(object):
    def collect(self):
        c = GaugeMetricFamily('zulip_server', 'Server Info', labels=['info'])
        a = GaugeMetricFamily('authentication_methods', 'Authentication Methods', labels=['auth'])
        r = json.loads(json.dumps(client.get_server_settings()))
        extract_values = ['zulip_version','zulip_feature_level', 'push_notifications_enabled','require_email_format_usernames','is_incompatible']
        for i in r:
            if i in extract_values:
              if type(r[i]) == bool:
                  value = int(r[i])
              else: value = r[i]
              c.add_metric([i], value)
        yield c

class UserCollector(object):
    def collect(self):
        r = json.loads(json.dumps(client.get_members()))
        yield CounterMetricFamily('zulip_user', 'Total user', value=(len(r['members'])))
        count_dict = {}
        for i in r['members']:
            for k, v in i.items():
                if v == True:
                    count_dict[k] = count_dict.get(k, 0) + 1
        yield CounterMetricFamily('zulip_user_bots', 'Total Bot accounts', value=(count_dict.get('is_bot',0)))
        yield CounterMetricFamily('zulip_user_admins', 'Total Admins accounts', value=(count_dict.get('is_admin',0)))
        yield CounterMetricFamily('zulip_user_guests', 'Total Guests accounts', value=(count_dict.get('is_guest',0)))
        yield CounterMetricFamily('zulip_user_active', 'Total Active accounts', value=(count_dict.get('is_active',0)))
        yield CounterMetricFamily('zulip_user_owners', 'Total Owners accounts', value=(count_dict.get('is_owner',0)))

class SubscriptionCollector(object):
    def collect(self):
        r = json.loads(json.dumps(client.list_subscriptions()))
        yield CounterMetricFamily('zulip_stream', 'Total Streams', value=(len(r['subscriptions'])))
        for x in r['subscriptions']:
          for k, v in x.items():
            t = type(v)
            if k != "name":
                if t == int or t == bool:
                  metrictemp = GaugeMetricFamily(f'zulip_stream_{k}', f'{k}', labels=["stream"])
                  metrictemp.add_metric([x['name']], int(v))
                  yield metrictemp


if __name__ == '__main__':
  try:
    logging.info('Starting..')
    logging.info('Grabbing metrics..')
    REGISTRY.register(SubscriptionCollector())
    REGISTRY.register(InfoCollector())
    REGISTRY.register(UserCollector())
    start_http_server(int(httpport))
    while True:
      sleep(int(frequency))
  except KeyboardInterrupt:
    logging.info("Exit, keyboard interrupt")
    exit(0)
