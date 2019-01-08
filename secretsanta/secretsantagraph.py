import collections
import random


class SecretSantaGraph:
    def __init__(self, families_to_members, members_to_families, old_connections):
        self.members_to_families = members_to_families
        self.families_to_members = families_to_members
        self.old_connections = old_connections

    def connection_is_valid(self, conn, connections):
        source_fam = self.members_to_families[conn.source]
        target_fam = self.members_to_families[conn.target]

        return (source_fam != target_fam
                and not self.old_connections.has(
                    conn.source,
                    conn.target)
                and not self.old_connections.has(
                    conn.target,
                    conn.source)
                and not conn.reverse() in connections)

    def random_connection(self,
                          connections,
                          source_queue,
                          target_queue,
                          year):

        source_index = len(source_queue) - 1
        target_index = len(target_queue) - 1

        change_sources = True

        while source_index >= 0 and target_index >= 0:
            source = source_queue[source_index]
            target = target_queue[target_index]

            conn = self.old_connections.make_weighted_conn(
                source,
                target,
                year
            )

            if self.connection_is_valid(conn, connections):
                if source_index < len(source_queue) - 1:
                    source_queue[source_index] = source_queue.pop()
                else:
                    source_queue.pop()

                if target_index < len(target_queue) - 1:
                    target_queue[target_index] = target_queue.pop()
                else:
                    target_queue.pop()

                return conn

            if change_sources:
                source_index -= 1
            else:
                target_index -= 1

            change_sources = not change_sources

        # Cannot generate valid connection
        return None

    def generate_connections(self, year):
        connections = set()
        members_keys = self.members_to_families.keys()
        members = list(members_keys)
        random.shuffle(members)
        source_queue = collections.deque(members)
        random.shuffle(members)
        target_queue = collections.deque(members)

        matched_sources = set()
        matched_targets = set()

        while len(source_queue) > 0 and len(target_queue) > 0:
            # Attempt to generate random connection
            # using unmatched nodes from queues
            conn = self.random_connection(connections,
                                          source_queue,
                                          target_queue,
                                          year)
            if conn is not None:
                matched_sources.add(conn.source)
                matched_targets.add(conn.target)
            else:
                # Could not generate connections, reattempt
                return self.generate_connections(year)

            connections.add(conn)

            if len(connections) == len(members):
                break

        return connections
