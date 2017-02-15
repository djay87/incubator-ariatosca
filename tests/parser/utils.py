# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from aria.parser.loading import UriLocation
from aria.parser.consumption import (
    ConsumptionContext,
    ConsumerChain,
    Read,
    Validate,
    Model,
    Types,
    Inputs,
    Instance
)
from aria.utils.imports import import_fullname

from tests import ROOT_DIR
from tests.resources import DIR


SERVICE_TEMPLATES_DIR = os.path.join(DIR, 'service-templates')


def get_example_uri(*args):
    return os.path.join(ROOT_DIR, 'examples', *args)


def get_test_uri(*args):
    return os.path.join(SERVICE_TEMPLATES_DIR, *args)


def create_context(uri,
                   loader_source='aria.parser.loading.DefaultLoaderSource',
                   reader_source='aria.parser.reading.DefaultReaderSource',
                   presenter_source='aria.parser.presentation.DefaultPresenterSource',
                   presenter=None,
                   debug=False):
    context = ConsumptionContext()
    context.loading.loader_source = import_fullname(loader_source)()
    context.reading.reader_source = import_fullname(reader_source)()
    context.presentation.location = UriLocation(uri) if isinstance(uri, basestring) else uri
    context.presentation.presenter_source = import_fullname(presenter_source)()
    context.presentation.presenter_class = import_fullname(presenter)
    context.presentation.print_exceptions = debug
    return context


def create_consumer(context, consumer_class_name):
    consumer = ConsumerChain(context, (Read, Validate))
    dumper = None
    if consumer_class_name == 'validate':
        dumper = None
    elif consumer_class_name == 'presentation':
        dumper = consumer.consumers[0]
    elif consumer_class_name == 'model':
        consumer.append(Model)
    elif consumer_class_name == 'types':
        consumer.append(Model, Types)
    elif consumer_class_name == 'instance':
        consumer.append(Model, Inputs, Instance)
    else:
        consumer.append(Model, Inputs, Instance)
        consumer.append(import_fullname(consumer_class_name))

    if dumper is None:
        # Default to last consumer
        dumper = consumer.consumers[-1]

    return consumer, dumper
