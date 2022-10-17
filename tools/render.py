#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author by me@xiexianbin.cn
# function: render README.md by template.
# date 2022-10-10

import os

import yaml
from jinja2 import Template

CURRENT_PATH = os.getcwd()

TABLE_HEADERS = [
  'Source',
  'Target(docker)',
  'Sync Account',
  'Sync Period',
  'Image Count',
  'Status']


class Render(object):
  def __init__(self):
    self.tpl_path = os.path.join(CURRENT_PATH, 'README.md.tpl')
    self.out_path = os.path.join(CURRENT_PATH, '../README.md')
    self.github_path = os.path.join(CURRENT_PATH, '../.github/workflows')

  def load_github_actions(self):
    actions = []
    for root, _, files in os.walk(self.github_path):
      for file in files:
        with open(os.path.join(root, file), 'r') as f:
          actions.append(yaml.load(f.read(), yaml.Loader))
    return actions

  def get_image_count(self, path):
    count = 0
    with open(path, 'r') as f:
      for line in f.readlines():
        if line.startswith('#') or line.strip() == '':
          continue
        else:
          count += 1
    return count

  def parse_github_action(self, action):
    for step in list(action["jobs"].values())[0]['steps']:
      if 'x-actions/python3-cisctl' in step['uses']:
        cron = action[True]['schedule'][0]['cron']
        file_ = '/'.join(step['env']['SRC_IMAGE_LIST_URL'].split('/')[-2:])
        source = file_.replace('.txt', '')
        _yaml_path = source.replace('/', '-')
        _target = step['env']['DEST_REPO'].replace('docker.io/', '')
        target = f'[{_target}](https://hub.docker.com/u/{_target})'
        sync_account = step['env']['DEST_TRANSPORT_USER']
        image_count = self.get_image_count(os.path.join(CURRENT_PATH, f'../{file_}'))
        status = f'[![{_target}](https://github.com/x-mirrors/gcr.io/actions/workflows/{_yaml_path}.yml/badge.svg)](https://github.com/x-mirrors/gcr.io/actions/workflows/{_yaml_path}.yml)'
        return True, source, target, sync_account, f'`{cron}`', image_count, status

    return False, None, None, None, None, None, None

  def _get_cron(self, action):
    return action[True]['schedule'][0]['cron']

  def render(self, mk_raw):
    with open(self.tpl_path, 'r') as in_file, open(self.out_path, 'w') as out_file:
      tpl = Template(in_file.read())
      out_file.write(tpl.render({'mk_raw': mk_raw}))

  def do(self):
    mk_lines = []
    mk_lines.append(f"|{'|'.join(TABLE_HEADERS)}|")
    mk_lines.append(f"|{'|'.join([':---' for _ in range(len(TABLE_HEADERS))])}|")

    actions = self.load_github_actions()
    target_lines = []
    for action in actions:
      result, source, target, sync_account, sync_period, image_count, status = self.parse_github_action(action)
      if result:
        target_lines.append({
          'source': source,
          'target': target,
          'sync_account': sync_account,
          'sync_period': sync_period,
          'image_count': image_count,
          'status': status,
        })

    target_lines = sorted(target_lines, key=lambda x: x['source'])
    for i in target_lines:
      mk_lines.append(f"|{'|'.join([i['source'], i['target'], i['sync_account'], i['sync_period'], str(i['image_count']), i['status']])}|")

    mk_raw = '\n'.join(mk_lines)
    self.render(mk_raw)


if __name__ == '__main__':
    Render().do()
