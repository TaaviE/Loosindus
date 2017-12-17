import random
import collections


class SecretSanta:
    def __init__(self, families, members, old_connections):
        self.families = families
        self.members = members
        self.oldConnections = old_connections

    def connection_is_valid(self, conn, connections):

        source_fam = self.families[conn.source]
        target_fam = self.families[conn.target]

        return (source_fam != target_fam
                and not self.oldConnections.has(
                    conn.source,
                    conn.target)
                and not self.oldConnections.has(
                    conn.target,
                    conn.source)
                and not conn.reverse() in connections)

    def random_connection(self,
                          connections,
                          source_queue,
                          target_queue,
                          year):

        s = len(source_queue) - 1
        t = len(target_queue) - 1

        change_sources = True

        while s >= 0 and t >= 0:
            source = source_queue[s]
            target = target_queue[t]

            conn = self.oldConnections.make_weighted_conn(
                source,
                target,
                year
            )

            if self.connection_is_valid(conn, connections):

                if s < len(source_queue) - 1:
                    source_queue[s] = source_queue.pop()
                else:
                    source_queue.pop()

                if t < len(target_queue) - 1:
                    target_queue[t] = target_queue.pop()
                else:
                    target_queue.pop()

                return conn

            if change_sources:
                s -= 1
            else:
                t -= 1

            change_sources = not change_sources

        # Cannot generate valid connection
        return None

    def generate_connections(self, year):
        connections = set()

        members = list(self.families.keys())
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
