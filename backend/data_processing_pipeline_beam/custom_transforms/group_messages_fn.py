# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import random
from apache_beam import GroupByKey, PTransform, WindowInto, WithKeys
from apache_beam.transforms.window import FixedWindows


class GroupMessagesByFixedWindows(PTransform):
  """A composite transform that groups Pub/Sub messages based on publish time

  and outputs a list of tuples, each containing a message and its publish time.
  """

  def __init__(self, window_size, num_shards=5):
    # Set window size to 60 seconds.
    self.window_size = int(window_size * 60)
    self.num_shards = num_shards

  def expand(self, pcoll):
    return (
        pcoll
        # Bind window info to each element using element timestamp (or publish time).
        | "Window into fixed intervals"
        >> WindowInto(FixedWindows(self.window_size))
        # Assign a random key to each windowed element based on the number of shards.
        | "Add key"
        >> WithKeys(lambda _: random.randint(0, self.num_shards - 1))
        # Group windowed elements by key. All the elements in the same window must fit
        # memory for this. If not, you need to use `beam.util.BatchElements`.
        | "Group by key" >> GroupByKey()
    )
