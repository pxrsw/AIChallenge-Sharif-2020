# بسم الله الرحمن الرحیم
import random

from model import *
from world import World


class AI:
    closest_enemy_path: Path

    def __init__(self):

        self.rows = 0
        self.cols = 0
        self.path_for_my_units = None

        self.state = 1
        self.state_of_tele = 1
        self.unit_that_have_damage_upgrade = None
        self.unit_that_have_range_upgrade = None
        self.dade = 0
        self.number_of_unit_in_best_cell = 0
        self.best_cell_we_can_choose = Cell()
        self.could_help_friend_while_hp_is_low = 1
        self.could_put_unit_on_friends_path = 1
        self.number_of_turns_after_friends_death = 0
        self.number_of_turns_after_last_put_to_friend = 0
        self.last_friend_unit_on_my_way = None
        self.turn_of_last_friend_unit_on_my_way = -1
        self.number_of_units_put_yet = 0
        self.closest_enemy_path = Path(-1, None, None)
        self.player_small = None
        self.player_large = None

        self.bayadbfrstm = False
        self.masir = Path(-1, None, None)
        self.baredoshman = 0
        self.barekhali = 0
        self.rukhalibfrstm = False
        self.masirekhali = Path(-1, None, None)
        self.faselealanedoshman = 1000

        self.ragbari = True

    # this function is called in the beginning for deck picking and pre process
    def pick(self, world: World):
        map = world.get_map()
        self.rows = map.row_num
        self.cols = map.col_num
        world.get_cast_spell_by_id(id=1.1)
        self.closest_enemy_path = world.get_me().paths_from_player[0]
        self.masir = world.get_me().paths_from_player[0]
        self.masirekhali = world.get_me().paths_from_player[0]

        # choosing hand
        all_base_units = world.get_all_base_units()

        # [base_unit for base_unit in all_base_units if not base_unit.is_flying]
        my_hand = [all_base_units[1], all_base_units[2], all_base_units[6], all_base_units[5], all_base_units[0]]

        # picking the chosen deck - rest of the deck will automatically be filled with random base_units
        world.choose_hand(base_units=my_hand)
        # (base_units=my_deck)

        # other preprocess
        if len(world.get_me().paths_from_player) > 1:
            self.path_for_my_units = world.get_friend().paths_from_player[0]
        else:
            self.path_for_my_units = world.get_friend().paths_from_player[0]

    # it is called every turn for doing process during the game
    def turn(self, world: World):
        self.dade = 0
        self.state_of_tele = 1

        if world.get_me().player_id > world.get_friend().player_id:
            self.player_small = world.get_friend()
            self.player_large = world.get_me()
        else:
            self.player_small = world.get_me()
            self.player_large = world.get_friend()


        all_base_units = world.get_all_base_units()
        print('#####################################')
        print('turn:')
        print(world.get_current_turn())

        myself = world.get_me()

        enemy_units = world.get_first_enemy().units
        enemy_units.append(world.get_second_enemy())

        # self.logger(world)

        my_units = world.get_me().units
        if world.get_current_turn() > 2:
            self.myfunction(world)
        elif world.get_current_turn() == 1:
            shortesttaking = self.minemasirbeshah(world)
            world.put_unit(base_unit=all_base_units[6], path=shortesttaking)
            world.put_unit(base_unit=all_base_units[1], path=shortesttaking)
            world.put_unit(base_unit=all_base_units[5], path=shortesttaking)
        elif world.get_current_turn() == 2:
            shortesttaking = self.minemasirbeshah(world)
            world.put_unit(base_unit=all_base_units[2], path=shortesttaking)
            world.put_unit(base_unit=all_base_units[0], path=shortesttaking)

        # for range upgrade
        if world.get_range_upgrade_number() > 0:

            if len(myself.units) > 0 and world.get_current_turn() > 3 * world.get_game_constants().turns_to_upgrade:
                units_max_range = []
                for unit_range in myself.units:
                    if unit_range.base_unit.type_id == 0:
                        units_max_range.append(unit_range)
                unit = self.get_max_hp(units_max_range)
                if unit is not None:
                    for i in range(0, world.get_range_upgrade_number()):
                        if world.get_me().range_upgraded_unit is not None:
                            unit = world.get_me().range_upgraded_unit
                        elif world.get_me().damage_upgraded_unit is not None:
                            unit = world.get_me().damage_upgraded_unit
                        else:
                            for item in my_units:
                                if item.range_level > 0 or item.damage_level > 0:
                                    unit = item
                        world.upgrade_unit_range(unit_id=unit.unit_id)
                    # self.unit_that_have_range_upgrade = unit
                    #     print(f'range dadam be {unit.unit_id}')

        # for damage upgrade
        if world.get_damage_upgrade_number() > 0:

            if len(myself.units) > 0 and world.get_current_turn() > 3 * world.get_game_constants().turns_to_upgrade:
                units_max_damage = []
                for unit_damage in myself.units:
                    if unit_damage.base_unit.type_id == 0:
                        units_max_damage.append(unit_damage)
                unit = self.get_max_hp(units_max_damage)
                if unit is not None:
                    for i in range(0, world.get_damage_upgrade_number()):
                        if world.get_me().range_upgraded_unit is not None:
                            unit = world.get_me().range_upgraded_unit
                        elif world.get_me().damage_upgraded_unit is not None:
                            unit = world.get_me().damage_upgraded_unit
                        else:
                            for item in my_units:
                                if item.range_level > 0 or item.damage_level > 0:
                                    unit = item
                        world.upgrade_unit_damage(unit_id=unit.unit_id)
                    # self.unit_that_have_damage_upgrade = unit
                    #     print(f'damage dadam be {unit.unit_id}')


        print('spell haye in turn')
        for spell in world.get_me().spells:
            print(f'spell {spell.type_id}')

        if world.get_first_enemy().is_alive() and world.get_second_enemy().is_alive():
            if self.check_spell_in_spells(myself.spells, 0):
                print('haste darimaaaaaaaaa---------------------------------------------------------------')
                haste_units = my_units + world.get_friend().units
                received_spell = self.spell_in_spells(myself.spells, 0)
                cell = self.return_best_cell_for_spell(world, received_spell)
                if len(haste_units) > 2 or world.get_current_turn() > world.get_game_constants().max_turns * 3 / 4:
                    print(f'number haste {self.number_of_unit_in_best_cell}')
                    for unit in haste_units:
                        if self.distance_from_king(unit.cell, world.get_first_enemy().king.center) < 7 or \
                                self.distance_from_king(unit.cell, world.get_second_enemy().king.center) < 7:
                            if unit.target is None and unit.player_id < 2:
                                last_unit = unit
                                received_spell = self.spell_in_spells(myself.spells, 0)
                                if last_unit.base_unit.type_id != 5:
                                    world.cast_area_spell(center=last_unit.cell, spell=received_spell)
                                    print(f'{last_unit.unit_id} haste ba shart king khord')
                        if self.number_of_unit_in_best_cell >= 4:
                            for item in world.get_area_spell_targets(center=cell, spell=received_spell):
                                if item.target is not None and item.player_id < 2:
                                    world.cast_area_spell(center=cell, spell=received_spell)
                                    # print(f'number haste {self.number_of_unit_in_best_cell}')
                                    # print(cell.row)
                                    # print(cell.col)
                        elif self.number_of_unit_in_best_cell >= 3 and \
                                world.get_current_turn() > world.get_game_constants().max_turns / 2:
                            for item in world.get_area_spell_targets(center=cell, spell=received_spell):
                                if item.target is not None and item.player_id < 2:
                                    world.cast_area_spell(center=cell, spell=received_spell)
                                    # print(f'number haste {self.number_of_unit_in_best_cell}')
                                    # print(cell.row)
                                    # print(cell.col)
                        elif 0 < len(my_units) < 3:
                            world.cast_area_spell(center=my_units[0].cell, spell=received_spell)
                            # print(f'number haste {self.number_of_unit_in_best_cell}')
                            print(cell.row)
                            print(cell.col)
        else:
            if self.check_spell_in_spells(myself.spells, 0):
                print('haste darimaaaaaaaaa---------------------------------------------------------------')
                haste_units = my_units + world.get_friend().units
                received_spell = self.spell_in_spells(myself.spells, 0)
                cell = self.return_best_cell_for_spell(world, received_spell)
                if len(haste_units) > 2 or world.get_current_turn() > world.get_game_constants().max_turns * 3 / 4:
                    print(f'number haste {self.number_of_unit_in_best_cell}')
                    for unit in haste_units:
                        if self.distance_from_king(unit.cell, world.get_first_enemy().king.center) < 7 or \
                                self.distance_from_king(unit.cell, world.get_second_enemy().king.center) < 7:
                            if unit.target is None:
                                last_unit = unit
                                received_spell = self.spell_in_spells(myself.spells, 0)
                                if last_unit.base_unit.type_id != 5:
                                    world.cast_area_spell(center=last_unit.cell, spell=received_spell)
                                    print(f'{last_unit.unit_id} haste ba shart king khord')
                        if self.number_of_unit_in_best_cell >= 4:
                            for item in world.get_area_spell_targets(center=cell, spell=received_spell):
                                if item.target is not None:
                                    world.cast_area_spell(center=cell, spell=received_spell)
                                    # print(f'number haste {self.number_of_unit_in_best_cell}')
                                    # print(cell.row)
                                    # print(cell.col)
                        elif self.number_of_unit_in_best_cell >= 3 and \
                                world.get_current_turn() > world.get_game_constants().max_turns / 2:
                            for item in world.get_area_spell_targets(center=cell, spell=received_spell):
                                if item.target is not None:
                                    world.cast_area_spell(center=cell, spell=received_spell)
                                    # print(f'number haste {self.number_of_unit_in_best_cell}')
                                    # print(cell.row)
                                    # print(cell.col)
                        elif 0 < len(my_units) < 3:
                            world.cast_area_spell(center=my_units[0].cell, spell=received_spell)
                            # print(f'number haste {self.number_of_unit_in_best_cell}')
                            print(cell.row)
                            print(cell.col)

        if self.check_spell_in_spells(myself.spells, 1):
            print('damage darimaaaaaaaaa---------------------------------------------------------------')
            # if len(my_units) > 1:
            #     last_unit = my_units[0].target
            #     if last_unit is not None:
            #         print(last_unit.unit_id)
            received_spell = self.spell_in_spells(myself.spells, 1)
            cell = self.return_best_cell_for_spell(world, received_spell)
            print(f'number damage {self.number_of_unit_in_best_cell}')
            if self.number_of_unit_in_best_cell >= 5:
                world.cast_area_spell(center=cell, spell=received_spell)
                print(cell.row)
                print(cell.col)
            elif self.number_of_unit_in_best_cell >= 4 and \
                    world.get_current_turn() >= world.get_game_constants().max_turns / 2:
                world.cast_area_spell(center=cell, spell=received_spell)
                print(cell.row)
                print(cell.col)
            elif self.number_of_unit_in_best_cell >= 3 and \
                    world.get_current_turn() >= world.get_game_constants().max_turns / 4 * 3:
                world.cast_area_spell(center=cell, spell=received_spell)
                print(cell.row)
                print(cell.col)


        if self.check_spell_in_spells(myself.spells, 2):
            print('heal darimaaaaaaaaa---------------------------------------------------------------')
            if len(my_units) > 2:
                last_unit = my_units[0]
                received_spell = self.spell_in_spells(myself.spells, 2)
                if last_unit.hp < last_unit.base_unit.max_hp - 1:
                    world.cast_area_spell(center=last_unit.cell, spell=received_spell)
                    print(f'{last_unit.unit_id} heal khord')

        if self.check_spell_in_spells(myself.spells, 3):
            print('tele darimaaaaaaaaa---------------------------------------------------------------')
            if self.check_unit_in_units(world.get_me().units, all_base_units[0]) and\
                    (world.get_damage_upgrade_number() + world.get_range_upgrade_number() > 2
                     or 69 < world.get_current_turn() < 90):
                print('tele midim b upgrade')
                if len(my_units) > 1:
                    last_unit = my_units[-1]
                    first_unit = my_units[0]
                    for item in my_units:
                        if item.range_level > 0 or item.damage_level > 0:
                            last_unit = item
                            if self.player_large.is_alive() and world.get_first_enemy().is_alive():
                                print('is alive for tele')
                                # path = world.get_shortest_path_to_cell(from_player=self.player_large,
                                #                                        cell=world.get_first_enemy().king.center)
                                path = self.player_large.paths_from_player[1]
                                size = len(path.cells)
                                cell = path.cells[(int((size + 1) / 2)) - 3]
                                print((int((size + 1) / 2)) - 3)
                                print(f'cell tele {cell}')
                                received_spell = self.spell_in_spells(myself.spells, 3)
                                for i in range((int((size + 1) / 2)) - 3, 5, -1):
                                    print('range cell')
                                    cell = path.cells[i]
                                    print(cell)
                                    if last_unit.base_unit.type_id == 0 and self.check_area(world, cell, 5):
                                        world.cast_unit_spell(unit=last_unit, path=path, cell=cell,
                                                              spell=received_spell)
                                        print(f'{last_unit.unit_id}raft max')
                                        break

            if self.check_unit_in_units(world.get_me().units, all_base_units[0]) and\
                    (self.check_number_of_spell(myself.spells, 3) > 1 or world.get_current_turn() > 100):
                if len(my_units) > 1:
                    print('tele turn 100 b bad')
                    last_unit = my_units[-1]
                    first_unit = my_units[0]
                    my_paths = myself.paths_from_player
                    path = my_paths[random.randint(0, len(my_paths) - 1)]
                    size = len(path.cells)
                    cell = path.cells[(int((size + 1) / 2)) - 3]
                    received_spell = self.spell_in_spells(myself.spells, 3)
                    if last_unit.base_unit.type_id != 4:
                        if self.distance_from_my_king(first_unit.cell, world) > self.distance_from_my_king(
                                path.cells[(int((size + 1) / 2)) - 3], world):
                            world.cast_unit_spell(unit=last_unit, path=path, cell=cell, spell=received_spell)
                            print(f'{last_unit.unit_id}raft max')
                        else:
                            world.cast_unit_spell(unit=last_unit, path=path, cell=first_unit.cell, spell=received_spell)
                            print(f'{last_unit.unit_id}raft khat')

        if world.get_first_enemy().is_alive() and world.get_second_enemy().is_alive():
            if self.check_spell_in_spells(myself.spells, 4):
                print('duplicate darimaaaaaaaaa---------------------------------------------------------------')
                received_spell = self.spell_in_spells(myself.spells, 4)
                cell = self.return_best_cell_for_spell(world, received_spell)
                print(f'number duplicate {self.number_of_unit_in_best_cell}')
                if self.number_of_unit_in_best_cell >= 3:
                    for unit in world.get_area_spell_targets(center=cell, spell=received_spell):
                        if unit.target is not None and unit.player_id < 2:
                            last_unit = unit
                            received_spell = self.spell_in_spells(myself.spells, 4)
                            world.cast_area_spell(center=cell, spell=received_spell)
                            print(f'{last_unit.unit_id} duplicate khord')
                elif self.number_of_unit_in_best_cell >= 2 and \
                        world.get_current_turn() > world.get_game_constants().max_turns / 2:
                    for unit in world.get_area_spell_targets(center=cell, spell=received_spell):
                        if unit.target is not None and unit.player_id < 2:
                            last_unit = unit
                            received_spell = self.spell_in_spells(myself.spells, 4)
                            world.cast_area_spell(center=cell, spell=received_spell)
                            print(f'{last_unit.unit_id} duplicate khord')
                elif 0 < len(my_units) < 3:
                    received_spell = self.spell_in_spells(myself.spells, 4)
                    world.cast_area_spell(center=my_units[0].cell, spell=received_spell)
                    # print(f'{last_unit.unit_id} duplicate khord')
        else:
            if self.check_spell_in_spells(myself.spells, 4):
                print('duplicate darimaaaaaaaaa---------------------------------------------------------------')
                received_spell = self.spell_in_spells(myself.spells, 4)
                cell = self.return_best_cell_for_spell(world, received_spell)
                print(f'number duplicate {self.number_of_unit_in_best_cell}')
                if self.number_of_unit_in_best_cell >= 3:
                    for unit in world.get_area_spell_targets(center=cell, spell=received_spell):
                        if unit.target is not None:
                            last_unit = unit
                            received_spell = self.spell_in_spells(myself.spells, 4)
                            world.cast_area_spell(center=cell, spell=received_spell)
                            print(f'{last_unit.unit_id} duplicate khord')
                elif self.number_of_unit_in_best_cell >= 2 and \
                        world.get_current_turn() > world.get_game_constants().max_turns / 2:
                    for unit in world.get_area_spell_targets(center=cell, spell=received_spell):
                        if unit.target is not None:
                            last_unit = unit
                            received_spell = self.spell_in_spells(myself.spells, 4)
                            world.cast_area_spell(center=cell, spell=received_spell)
                            print(f'{last_unit.unit_id} duplicate khord')
                elif 0 < len(my_units) < 3:
                    received_spell = self.spell_in_spells(myself.spells, 4)
                    world.cast_area_spell(center=my_units[0].cell, spell=received_spell)
                    # print(f'{last_unit.unit_id} duplicate khord')

        if self.check_spell_in_spells(myself.spells, 5):
            print('poison darimaaaaaaaaa---------------------------------------------------------------')
            # if len(my_units) > 0:
            #     last_unit = my_units[0].target
            #     if last_unit is not None:
            #         print(last_unit.unit_id)
            received_spell = self.spell_in_spells(myself.spells, 5)
            cell = self.return_best_cell_for_spell(world, received_spell)
            print(f'number poison {self.number_of_unit_in_best_cell}')
            if self.number_of_unit_in_best_cell >= 5:
                world.cast_area_spell(center=cell, spell=received_spell)
                print(cell.row)
                print(cell.col)
            elif self.number_of_unit_in_best_cell >= 4 and \
                    world.get_current_turn() >= world.get_game_constants().max_turns / 2:
                world.cast_area_spell(center=cell, spell=received_spell)
                print(cell.row)
                print(cell.col)
            elif self.number_of_unit_in_best_cell >= 3 and \
                    world.get_current_turn() >= world.get_game_constants().max_turns / 4 * 3:
                world.cast_area_spell(center=cell, spell=received_spell)
                print(cell.row)
                print(cell.col)


    def end(self, world: World, scores):
        print("end started!")
        print("My score:", scores[world.get_me().player_id])

    # added function
    def get_max_hp(self, units):
        max_hp = 0
        if len(units) > 0:
            max_hp_unit_select = units[0]
            for max_hp_unit in units:
                if max_hp_unit.hp >= max_hp and max_hp_unit.base_unit.type_id != 4:
                    max_hp = max_hp_unit.hp
                    max_hp_unit_select = max_hp_unit
            if max_hp_unit_select is not None:
                return max_hp_unit_select
        else:
            return None

    def get_max_damage(self, units):
        max_damage = 0
        if len(units) > 0:
            max_damage_unit_select = units[0]
            for max_damage_unit in units:
                if max_damage_unit.attack >= max_damage:
                    max_damage = max_damage_unit.attack
                    max_damage_unit_select = max_damage_unit
            if max_damage_unit_select is not None:
                return max_damage_unit_select
        else:
            return None

    def get_max_range(self, units):
        max_range = 0
        if len(units) > 0:
            max_range_unit_select = units[0]
            for max_range_unit in units:
                if max_range_unit.range >= max_range:
                    max_range = max_range_unit.range
                    max_range_unit_select = max_range_unit
            if max_range_unit_select is not None:
                return max_range_unit_select
        else:
            return None

    def find_max_hp_between_our_unit(self, my_units):
        max_hp = 0
        unit_of_max_hp = my_units[0]
        for unit in my_units:
            if unit.hp > max_hp:
                max_hp = unit.hp
                unit_of_max_hp = unit
        return unit_of_max_hp

    def return_best_cell_for_spell(self, world, received_spell):
        self.number_of_unit_in_best_cell = 0
        self.best_cell_we_can_choose = 0
        map = world.get_map()
        row_of_map = map.row_num
        column_of_map = map.col_num
        row_of_best_cell = 0
        col_of_best_cell = 0

        for column_index in range(0, column_of_map):
            for row_index in range(0, row_of_map):
                cell_for_our_loop = Cell(row_index, column_index)  # cell e marboot be in halghe
                if self.number_of_unit_in_best_cell < len(
                        world.get_area_spell_targets(row=row_index, col=column_index, center=cell_for_our_loop,
                                                     spell=received_spell)):
                    self.number_of_unit_in_best_cell = len(
                        world.get_area_spell_targets(row=row_index, col=column_index, center=cell_for_our_loop,
                                                     spell=received_spell))

                    row_of_best_cell = row_index
                    col_of_best_cell = column_index

        self.best_cell_we_can_choose = Cell(row_of_best_cell, col_of_best_cell)

        return self.best_cell_we_can_choose

    def last_unit_enemy(self, units_1, units_2):
        units = units_1 + units_2
        return units[-1]

    def check_unit_in_hand(self, hand, unit):
        for item in hand:
            if item.type_id == unit.type_id:
                return True
        return False

    def check_unit_in_units(self, units, unit):
        for item in units:
            if item.base_unit.type_id == unit.type_id:
                return True
        return False

    def check_spell_in_spells(self, spells, spell_type_id):
        for item in spells:
            if item.type_id == spell_type_id:
                return True
        return False

    def spell_in_spells(self, spells, spell_type_id):
        for item in spells:
            if item.type_id == spell_type_id:
                return item

    def distance_from_my_king(self, cell, world):
        return abs(cell.col - world.get_me().king.center.col) + abs(cell.row - world.get_me().king.center.row)

    def logger(self, world):
        f = self.f
        f.write('Enemy Units:\n')
        first_enemy_units = world.get_first_enemy().units
        for unit in first_enemy_units:
            if type(unit) == Unit:
                f.write(
                    f'Id: {unit.unit_id}    Cell: ({unit.cell.row}, {unit.cell.col})       BaseUnit: {unit.base_unit.type_id}      HP: {unit.hp}      Spells: {unit.affected_spells} 1st enemy\n')
        second_enemy_units = world.get_second_enemy().units
        for unit in second_enemy_units:
            if type(unit) == Unit:
                f.write(
                    f'Id: {unit.unit_id}    Cell: ({unit.cell.row}, {unit.cell.col})        BaseUnit: {unit.base_unit.type_id}      HP: {unit.hp}      Spells: {unit.affected_spells} 2nd enemy\n')
        f.write('\n')

        f.write('My Units:\n')
        my_units = world.get_me().units
        for unit in my_units:
            if type(unit) == Unit:
                f.write(
                    f'Id: {unit.unit_id}    Cell: ({unit.cell.row}, {unit.cell.col})        BaseUnit: {unit.base_unit.type_id}      HP: {unit.hp}      Spells: {unit.affected_spells} \n')
        f.write('\n')

        f.write('Friend Units:\n')
        friend_units = world.get_friend().units
        for unit in friend_units:
            if type(unit) == Unit:
                f.write(
                    f'Id: {unit.unit_id}    Cell: ({unit.cell.row}, {unit.cell.col})        BaseUnit: {unit.base_unit.type_id}      HP: {unit.hp}      Spells: {unit.affected_spells} \n')
        f.write('\n')

    def check_friends_king(self, world):
        self.number_of_turns_after_last_put_to_friend += 1
        if not world.get_friend().king.is_alive:
            self.number_of_turns_after_friends_death += 1

        if self.number_of_turns_after_friends_death <= 3 and self.number_of_turns_after_friends_death > 0:
            if not self.put_the_most_damage_on_friend_path(world):
                self.put_the_cheapest_on_friend_path(world)
        elif self.number_of_turns_after_friends_death > 4:
            # print(f'{self.number_of_turns_after_last_put_to_friend} turns after friends last put')
            if self.number_of_turns_after_last_put_to_friend >= 4:
                if not self.put_the_most_damage_on_friend_path(world):
                    self.put_the_cheapest_on_friend_path(world)

    def put_the_cheapest_on_friend_path(self, world):
        cheapest_base_unit = world.get_me().hand[0]
        for base_unit in world.get_me().hand:
            if base_unit.ap < cheapest_base_unit.ap:
                cheapest_base_unit = base_unit
        if world.get_me().ap >= cheapest_base_unit.ap:
            world.put_unit(base_unit=cheapest_base_unit, path=world.get_friend().paths_from_player[0])
            self.number_of_turns_after_last_put_to_friend = 0
            return True
        return False

    def put_the_most_damage_on_friend_path(self, world):
        hand = world.get_me().hand
        sorted_hand = sorted(hand, key=lambda x: x.base_attack, reverse=True)
        my_ap = world.get_me().ap
        for base_unit in sorted_hand:
            if base_unit.ap <= my_ap:
                world.put_unit(base_unit=base_unit, path=world.get_friend().paths_from_player[0])
                self.number_of_turns_after_last_put_to_friend = 0
                return True
        return False

    def choose_and_put_unit(self, world, all_base_units):
        if world.get_current_turn() == 1:
            self.dade = 1
            world.put_unit(base_unit=all_base_units[1], path=world.get_me().paths_from_player[0])
            world.put_unit(base_unit=all_base_units[5], path=world.get_me().paths_from_player[0])

        if self.check_unit_in_hand(world.get_me().hand,
                                   all_base_units[0]) and self.dade == 0 and world.get_me().ap >= 4:
            world.put_unit(base_unit=all_base_units[0], path=world.get_me().paths_from_player[0])
            self.dade = 1

        if self.check_unit_in_hand(world.get_me().hand,
                                   all_base_units[1]) and self.dade == 0 and world.get_me().ap >= 3:
            world.put_unit(base_unit=all_base_units[1], path=world.get_me().paths_from_player[0])
            self.dade = 1

        if self.check_unit_in_hand(world.get_me().hand,
                                   all_base_units[6]) and self.dade == 0 and world.get_me().ap >= 2:
            world.put_unit(base_unit=all_base_units[6], path=world.get_me().paths_from_player[0])
            self.dade = 1

        if self.check_unit_in_hand(world.get_me().hand,
                                   all_base_units[2]) and self.dade == 0 and world.get_me().ap >= 4:
            world.put_unit(base_unit=all_base_units[2], path=world.get_me().paths_from_player[0])
            self.dade = 1

        if self.check_unit_in_hand(world.get_me().hand,
                                   all_base_units[5]) and self.dade == 0 and world.get_me().ap >= 3:
            world.put_unit(base_unit=all_base_units[5], path=world.get_me().paths_from_player[0])
            self.dade = 1

    '''agar yaremun roo masire ma chizi gozasht, ma ham roo masiresh yeki bezarim'''

    def should_put_unit_on_friends_path(self, world):
        if not self.could_put_unit_on_friends_path:
            # print('''agar as serie ghabl uniti moonde ke nazashti, bezar''')
            if self.put_the_most_damage_on_friend_path(world):
                # print('''agar tunest bezare''')
                self.could_put_unit_on_friends_path = 1

        if len(world.get_friend().units) > 0:
            friends_last_unit = world.get_friend().units[-1]
            my_paths = world.get_me().paths_from_player
            if self.last_friend_unit_on_my_way != None:
                # print('''Agar ta be hal roo masire man unit gozashte bud''')
                if self.last_friend_unit_on_my_way.unit_id != friends_last_unit.unit_id:
                    # print('''agar id e un ghablie ba id e akharin uniti ke tu bazi gozashte yeki nabud''')
                    '''(yani unit jadid gozashte bud)'''
                    if friends_last_unit.path == world.get_friend().path_to_friend or friends_last_unit.path in my_paths:
                        # print('''agar in jadide roo masire man bud''')
                        self.last_friend_unit_on_my_way = friends_last_unit  # update kon uno
                        if self.put_the_most_damage_on_friend_path(world):
                            # print('''agar poolet resid o gozashti''')
                            self.could_put_unit_on_friends_path = 1
                        else:
                            # print('''agar poolet naresid o nazashti''')
                            self.could_put_unit_on_friends_path = 0

            elif self.last_friend_unit_on_my_way == None:
                if friends_last_unit.path == world.get_friend().path_to_friend or friends_last_unit.path in my_paths:
                    '''agar ru masire man gozashte bud doostam'''
                    self.last_friend_unit_on_my_way = friends_last_unit
                    if self.put_the_most_damage_on_friend_path(world):
                        '''agar poolet resid o gozashti'''
                        self.could_put_unit_on_friends_path = 1
                    else:
                        '''agar poolet naresid o nazashti'''
                        self.could_put_unit_on_friends_path = 0

    def friend_is_empty(self, world):
        if len(world.get_friend().units) == 0:
            return True
        return False

    def help_friend(self, world):
        # print(f'number of turns after last put on friends way {self.number_of_turns_after_last_put_to_friend}')
        if self.number_of_turns_after_last_put_to_friend >= 3:
            if self.put_the_most_damage_on_friend_path(world):
                self.could_help_friend_while_hp_is_low = 1
                # print('could help')
            else:
                # print("couldn't help")
                self.could_help_friend_while_hp_is_low = 0

    def get_friend(self, world, player):
        if player.player_id == 0:
            return world.get_player_by_id(2)
        elif player.player_id == 1:
            return world.get_player_by_id(3)
        elif player.player_id == 2:
            return world.get_player_by_id(0)
        elif player.player_id == 3:
            return world.get_player_by_id(1)

    def put_x_units_on_closest(self, world, x):
        if self.number_of_units_put_yet == x:
            self.closest_enemy_path = self.get_closest_enemy_path(world, world.get_me())
            self.number_of_units_put_yet = 0
        if self.number_of_units_put_yet < x:
            if self.put_unit_on_path(world, self.closest_enemy_path):
                print(f'put on path {self.closest_enemy_path.id}')
                self.number_of_units_put_yet += 1

    def put_unit_on_path(self, world, path):
        # 6>0>1>2>5
        all_base_units = world.get_all_base_units()
        if self.check_unit_in_hand(world.get_me().hand, all_base_units[6]) and world.get_me().ap >= 2:
            world.put_unit(base_unit=all_base_units[6], path=path)
            # print(f"put {6}")
            return True
        elif self.check_unit_in_hand(world.get_me().hand, all_base_units[0]) and world.get_me().ap >= 4:
            world.put_unit(base_unit=all_base_units[0], path=path)
            # print(f"put {0}")
            return True
        elif self.check_unit_in_hand(world.get_me().hand, all_base_units[1]) and world.get_me().ap >= 3:
            world.put_unit(base_unit=all_base_units[1], path=path)
            # print(f"put {1}")
            return True
        elif self.check_unit_in_hand(world.get_me().hand, all_base_units[2]) and world.get_me().ap >= 4:
            world.put_unit(base_unit=all_base_units[2], path=path)
            # print(f"put {2}")
            return True
        elif self.check_unit_in_hand(world.get_me().hand, all_base_units[5]) and world.get_me().ap >= 3:
            world.put_unit(base_unit=all_base_units[5], path=path)
            # print(f"put {5}")
            return True

        return False

    def get_closest_enemy_path_and_dist(self, world, player):
        print('----------daram masir o fasele nazdik tarin doshman ro hesab mikonam')
        paths = player.paths_from_player
        nearest_cell = paths[0].cells[-1]
        nearest_path = paths[0]
        min_fasele = 10000
        liste_rah_o_fasle = []
        for path in paths:
            cells = path.cells
            for cell in cells:
                # print(f'in cell ({cell.row} , {cell.col})')
                for unit in cell.units:
                    # print(f'on unit {unit.unit_id}')
                    if (unit.player_id != player.player_id) and (unit.player_id != world.get_friend().player_id):
                        # print('the unit is an enemy')
                        fasele = self.faselecelltaking(world, cell)
                        if fasele < min_fasele:
                            print(f'----------min fasele ta nazdik tarin doshman ta alan ({min_fasele}) bude ke bozorgtar az fasele in yekie({fasele})')
                            '''havaset bashe i < index ro didi faghat <= ro nazadi'''
                            min_fasele = fasele
                            nearest_cell = cell
                            nearest_path = path
                            tup = (path, fasele, cells.index(cell))
                            liste_rah_o_fasle.append(tup)
                            print(f'----------nearest enemy of path {path.id} is on cell ({cell.row} , {cell.col})')
        t = (nearest_path, min_fasele, liste_rah_o_fasle)
        print(f'----------path e nazdik tarin doshman: {t[0].id} va min e fasele: {min_fasele}')

        return t

    def myfunction(self, world):

        '''------------------------------------------------------------------------------------------------------ '''
        '''PARSA VA MEHDI SHOMA AGAR KHASTID CHIZIO AVAZ KONID, FAGHAT BE INA DAST BEZANID'''
        FASELE_DEFA = 12
        '''------------------------------------------------------------------------------------------------------ '''

        if world.get_me().player_id < world.get_friend().player_id:
            print('''man ghavie am''')
            self.ghavi(world, FASELE_DEFA)
        else:
            print('''man zaeif am''')
            if self.zaeif(world, FASELE_DEFA):
                return


        # minealan = self.get_closest_enemy_path_and_dist(world, world.get_me(), FASELE_DEFA)
        # minerah = Path(-1,[])
        # minefasele = 10000
        # liste_raha = minealan[2]  #(rah, fasle Manhattani, index cell )
        # i = 0
        # for tuple in liste_raha:
        #     print("TUPLE IS:")
        #     print(tuple)
        #     path = tuple[0]
        #     fasele = tuple[1]
        #     index = tuple[2]
        #     for i in range(1,index):
        #         for unit in path.cells[i].units:
        #             if unit.player_id == world.get_me().player_id:
        #                 print(f'rooye cell e ({unit.cell.row},{unit.cell.col}) ')
        #                 liste_raha = [x for x in liste_raha if x != tuple]
        #     i += 1
        # for tuple in liste_raha:
        #     path = tuple[0]
        #     fasele = tuple[1]
        #     index = tuple[2]
        #     if fasele < minefasele and fasele < FASELE_DEFA:
        #         minefasele = fasele
        #         minerah = path
        # if minerah.id != -1:
        #     if self.put_defa(world, minerah):
        #         print('invar khali bud ferestadam')
        #
        # if minealan[1] <= FASELE_DEFA:
        #     if self.put_defa(world, minealan[0]):
        #         print(f'defa kardam roo masire {minealan[0].id}')
        #         return
        #
        # if self.put_unit_on_path(world, self.aslieyar_ya_shortest(world)):
        #     print('roo masire yar ya shortest gozashtam')

    def get_masirekhali(self, world):
        print('---daram masire khali peyda mikonam')
        '''-------------------------------------------------------------------------------------------------------'''
        MAXIMUM_OF_MASIRE_KHALLI = (world.get_game_constants().max_turns - world.get_current_turn()) - 5
        '''-------------------------------------------------------------------------------------------------------'''
        print(f'---MAXIMUM_OF_MASIRE_KHALI = {MAXIMUM_OF_MASIRE_KHALLI}')
        masire_khali = []
        for path in world.get_me().paths_from_player:
            cut = 0
            print(f'---masire man: {path.id}')
            for cell in path.cells:
                for unit in cell.units:
                    if unit.player_id == world.get_first_enemy().player_id or unit.player_id == world.get_second_enemy().player_id and world.get_second_enemy().king.is_alive:
                        print("---doshman hast in ru")
                        if cell != world.get_first_enemy().king.center and cell != world.get_second_enemy().king.center:
                            cut = 1
                            print('---shah ham nabud. sarbaze yani. dg in masir ro nagard. khali nist')
                            break
                if cut == 1:
                    print('---baghie cell haye path ro lazem nist begardi')
                    break
            if cut == 0:
                print('''---yani masir khali bude''')
                tuple = (path, len(path.cells))
                masire_khali.append(tuple)

        for path in world.get_friend().paths_from_player:
            cut = 0
            print(f'---masire yaram: {path.id}')
            for cell in path.cells:
                for unit in cell.units:
                    if unit.player_id == world.get_first_enemy().player_id or unit.player_id == world.get_second_enemy().player_id :
                        print("---doshman hast in ru")
                        if cell != world.get_first_enemy().king.center and cell != world.get_second_enemy().king.center:
                            cut = 1
                            print('---shah ham nabud. sarbaze yani. dg in masir ro nagard. khali nist')
                            break
                if cut == 1:
                    print('---baghie cell haye path ro lazem nist begardi')
                    break
            if cut == 0:
                print('''---yani masir khali bude''')
                tuple = (path, len(path.cells) + len(world.get_me().path_to_friend.cells))
                masire_khali.append(tuple)

        mintuple = (-1, 10000)
        for tuple in masire_khali:
            if tuple[1] <= mintuple[1]:
                mintuple = tuple

        if mintuple[1] < MAXIMUM_OF_MASIRE_KHALLI:
            return mintuple[0]
        return Path(-1, [])

    def get_masireaslieyar(self, world):
        print('-----daram masire aslie yar ro peyda mikonam')
        units = world.get_friend().units
        paths = []
        for path in world.get_map().paths:
            paths.append([path, 0])
        for unit in units:
            for item in paths:
                if item[0].id == unit.path.id:
                    item[1] += 1
        max = 0
        path = None
        for item in paths:
            if item[1] >= max:
                max = item[1]
                path = item[0]
        print(f'-----masire aslie yar: {path.id}')
        if max == 0:
            print("-----yar masire asli nadasht. be masire 0sh ferestadim")
            path = world.get_friend().paths_from_player[0]
        return path

    def fasele2tacell(self, avali, dovomi):
        return abs(avali.row - dovomi.row) + abs(avali.col - dovomi.col)

    def faselecelltaking(self, world, cell):
        row = world.get_me().king.center.row
        col = world.get_me().king.center.col
        king_area = [Cell(row - 1, col - 1), Cell(row - 1, col), Cell(row - 1, col + 1), Cell(row, col - 1),
                     Cell(row, col), Cell(row, col + 1), Cell(row + 1, col - 1), Cell(row + 1, col),
                     Cell(row + 1, col + 1)]
        min = 5000
        for khoone in king_area:
            fasele = self.fasele2tacell(cell, khoone)
            if fasele < min:
                min = fasele
        return min

    def distance_from_king(self, cell, king_cell):
        return abs(cell.col - king_cell.col) + abs(cell.row - king_cell.row)

    def minemasirbeshah(self, world):

        print('-----daram min e masir be shah ro peyda mikonam')
        shortest = world.get_me().paths_from_player[0]
        length = 10000#len(world.get_me().paths_from_player[0].cells)
        for path in world.get_me().paths_from_player:
            pathlen = len(path.cells)
            print(f'-----daram masire {path.id} ro barresi mikonam k shortest king hast ya na')
            print(f'-----cell e akhare path: ({path.cells[-1].row}, {path.cells[-1].col})')
            if (path.cells[-1] == world.get_second_enemy().king.center and world.get_second_enemy().king.is_alive) or \
                    (path.cells[-1] == world.get_first_enemy().king.center and world.get_first_enemy().king.is_alive):
                print('-----tahe masire shortest ye shahe zende st')
                if pathlen < length:
                    print('-----in yeki masir kootah tar bud.')
                    length = pathlen
                    shortest = path
        lenemasirbedoost = len(world.get_me().path_to_friend.cells)
        for path in world.get_friend().paths_from_player:
            pathlen = len(path.cells)
            if pathlen + lenemasirbedoost < length:
                length = pathlen + lenemasirbedoost
                shortest = path
        print(f'-----shorteste king {shortest.id} ba toole {length}')
        return shortest

    def put_defa(self, world, path):
        # 6>0>1>5>2
        all_base_units = world.get_all_base_units()
        if self.check_unit_in_hand(world.get_me().hand, all_base_units[6]) and world.get_me().ap >= 2:
            world.put_unit(base_unit=all_base_units[6], path=path)
            # print(f"put {6}")
            return True
        elif self.check_unit_in_hand(world.get_me().hand, all_base_units[0]) and world.get_me().ap >= 4:
            world.put_unit(base_unit=all_base_units[0], path=path)
            # print(f"put {0}")
            return True
        elif self.check_unit_in_hand(world.get_me().hand, all_base_units[1]) and world.get_me().ap >= 3:
            world.put_unit(base_unit=all_base_units[1], path=path)
            # print(f"put {1}")
            return True
        elif self.check_unit_in_hand(world.get_me().hand, all_base_units[2]) and world.get_me().ap >= 4:
            world.put_unit(base_unit=all_base_units[2], path=path)
            # print(f"put {2}")
            return True
        elif self.check_unit_in_hand(world.get_me().hand, all_base_units[5]) and world.get_me().ap >= 3:
            world.put_unit(base_unit=all_base_units[5], path=path)
            # print(f"put {5}")
            return True

        return False

    def aslieyar_ya_shortest(self, world):
        shortest = self.minemasirbeshah(world)
        print(f'---------------toole shortest e king: {len(shortest.cells)}')
        print(f"---------------toole masriam ta yar: {len(world.get_me().path_to_friend.cells)}")
        if len(shortest.cells) <= len(world.get_me().path_to_friend.cells):
            print("---------------Shortest e king ro entekhab kardam")
            return shortest
        print('---------------masire aslie yar gozashtam')
        return self.get_masireaslieyar(world)

    def put_xk(self, world, path):
        all_base_units = world.get_all_base_units()
        if self.check_unit_in_hand(world.get_me().hand, all_base_units[6]) and world.get_me().ap >= 2:
            world.put_unit(base_unit=all_base_units[6], path=path)
            # print(f"put {6}")
            return True
        elif self.check_unit_in_hand(world.get_me().hand, all_base_units[1]) and world.get_me().ap >= 3:
            world.put_unit(base_unit=all_base_units[1], path=path)
            # print(f"put {1}")
            return True
        return False

    def number_of_enemies(self, world, path, FASELE_DEFA):
        counter = 0
        for cell in path.cells:
            if self.faselecelltaking(world, cell) < FASELE_DEFA:
                for unit in cell.units:
                    if unit.player_id == world.get_first_enemy().player_id or unit.player_id == world.get_second_enemy().player_id:
                        counter += 1
        print(f'---------------Tedade unit haye DOSHMAN rooye masire {path.id}: {counter}')
        return counter

    def number_of_my_units(self, world, path, FASELE_DEFA):
        counter = 0
        for cell in path.cells:
            if self.faselecelltaking(world, cell) < FASELE_DEFA:
                for unit in cell.units:
                    if unit.player_id == world.get_me().player_id:
                        counter+=1
        print(f'---------------Tedade unit haye MAN rooye masire {path.id}: {counter}')
        return counter

    def difference(self, world, path, FASELE_DEFA):
        '''in adad agar == 0 she yani unit haye ma 2 ta bishtar az unit haye doshmane'''
        '''har chi in adade bishtar bashe yani olaviate ferestaden bishtare'''
        dif = 0
        units = self.number_of_my_units(world, path, FASELE_DEFA)
        enemies = self.number_of_enemies(world, path, FASELE_DEFA)
        if enemies > 0:
            print(f'----------enemy bud ru masire{path.id}')
            dif = enemies - units + 3
        else:
            print(f'----------aslan enemy nabud ru masire {path.id}')
            dif = enemies - units
        if enemies > 0 and units == 0:
            dif = 1000
        print(f'----------dif e masire {path.id}: {dif}')
        return dif

    def get_max_difference_path(self,world, FASELE_DEFA):
        best_path = Path(-1, [])
        maximum = 0
        for path in world.get_me().paths_from_player:
            dif = self.difference(world, path, FASELE_DEFA)
            if dif > 0 and dif > maximum:
                print(f'----dif({dif}) > 0 va dif({dif}) > maximum{maximum}')
                best_path = path
                maximum = dif
        print(f'----best_path vase dif: {best_path.id}')
        return best_path

    def defa(self, world, FASELE_DEFA):
        path = self.get_max_difference_path(world, FASELE_DEFA)
        print(f'--masire defa: {path.id}')
        if path.id != -1:
            if self.put_unit_on_path(world, path):
                print('--defa kardam')
                return True
        print('--nashod defa konam')
        return False

    def xk(self,world,FASELE_DEFA):
        minealan = self.get_closest_enemy_path_and_dist(world, world.get_me())
        '''agar fasele zire 8 kasi nabud in karo kon tu 15k va 15k+1:'''
        if minealan[1] > FASELE_DEFA:
            '''agar turn 10k ya 10k+1 bud, saay mikonim ru masire khali unit beferestim.'''
            if world.get_current_turn() % 10 == 1 or world.get_current_turn() % 10 == 0:
                print('---turn e 10k ya 10k+1')
                masirekhali = self.get_masirekhali(world)
                if len(masirekhali.cells) < world.get_game_constants().max_turns - world.get_current_turn() \
                    and self.inshahekie(world, masirekhali).is_alive:
                    """dar soorati roo masire khali mifereste ke munde bashe turn e kafi """
                    if masirekhali.id != -1:
                        print('---masire khali daram')
                        if self.put_xk(world, masirekhali):
                            print(f'---unit gozashtam ru masire khalie {masirekhali.id}')
                            return True
                        else:
                            print('---vali pool ya unit e monaseb nadashtam ru masire khali bzarm')
                    else:
                        print('---masiri khali nabud. pas edame midam be myfunction')

        return False

    def zaeif(self, world, FASELE_DEFA):

        print('XK')
        if self.xk(world, FASELE_DEFA):
            return True
        print('DEFA')
        if self.defa(world, FASELE_DEFA):
            return True
        print('MASIRE ASLIE YAR')
        masireaslieyar = self.get_masireaslieyar(world)
        if world.get_game_constants().max_turns - world.get_current_turn() -5 > len(world.get_me().path_to_friend.cells)  and\
                self.inshahekie(world,masireaslieyar).is_alive:
            if self.put_unit_on_path(world, masireaslieyar):
                return True
        else:
            if self.put_unit_on_path(world, self.minemasirbeshah(world)):
                return True
        return False

    def ghavi(self, world, FASELE_DEFA):
        print('D E F A')
        if self.defa(world, FASELE_DEFA):
            return True
        print(f'R A G B A R I   AP:{world.get_me().ap}')
        # if self.put_unit_on_path(world,self.minemasirbeshah(world)):
        if self.put_ragbari(world):
            print('RAGBARI true dad')
            return True
        print('RAGBARI false dad yani dare por mikone')
        return False

    def check_number_of_spell(self, spells, spell_type_id):
        counter = 0
        for item in spells:
            if item.type_id == spell_type_id:
                counter += 1
        return counter

    def check_area(self, world, cell, FASELE):
        area_cells = self.get_area(world, cell, FASELE)
        for cell in area_cells:
            for unit in cell.units:
                if unit.player_id == world.get_first_enemy().player_id or \
                        unit.player_id == world.get_second_enemy().player_id:
                    return False
        return True

    def get_area(self, world, cell, FASELE):
        area_list = []
        for row in range(0, world.get_map().row_num):
            for col in range(0, world.get_map().col_num):
                if self.fasele2tacell(cell, Cell(row, col)) <= FASELE:
                    area_list.append(Cell(row, col))
                    print(f'cell({row},{col}) is in area of {cell} and {FASELE}')
        return area_list

    def inshahekie(self, world, path):
        if path.cells[-1] == world.get_first_enemy().king.center:
            print(f'cell e ({path.cells[-1].row}, {path.cells[-1].col}) vase shahe {world.get_first_enemy().player_id}')
            return world.get_first_enemy().king
        print(f'cell e ({path.cells[-1].row}, {path.cells[-1].col}) vase shahe {world.get_second_enemy().player_id}')
        return world.get_second_enemy().king

    def get_kootahtarinmasirbeinshah(self, world, king):
        '''ye shahi ro midi behesh. kootahtarin masir az khodet va yaret be un shahe ro mide behet'''
        shortest = Path(-1, [])
        length = 10000
        best = []
        for path in world.get_me().paths_from_player:
            if self.inshahekie(world, path) == king:
                best.append(path)
        for path in best:
            if len(path.cells) < length:
                shortest = path
                length = len(path.cells)
        for path in world.get_friend().paths_from_player:
            if self.inshahekie(world, path) == king:
                best.append(path)
        for path in best:
            if len(path.cells)+len(world.get_me().path_to_friend.cells) < length:
                shortest = path
                length = len(path.cells)+len(world.get_me().path_to_friend.cells)
        print(f'--shortest be shahe {king.player_id} masire {shortest.id} hastesh')
        return shortest

    def put_ragbari(self, world):
        max_ap = world.get_game_constants().max_ap
        if world.get_me().ap >= max_ap - 1:
            self.ragbari = True
        ap = world.get_me().ap
        if self.ragbari == True:
            if self.put_unit_on_path(world, self.minemasirbeshah(world)):
                return True
            else:
                self.ragbari = False
                return False