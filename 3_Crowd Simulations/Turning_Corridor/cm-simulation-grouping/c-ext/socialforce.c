#include "socialforce.h"

static int group_num;
static int * group_population_count; //array to contain group size of each group --default = -1
static Pedestrian * group_pedestrians; //array to contain whole pedestrians of different groups 

static double timestep; //parameter to compute obstacle force
static double total_simulation_time; //total time that has been simulated


static Wall * walls; //walls
static Py_ssize_t w_count; //wall count
static double wall_repulsive_strength;
static double wall_repulsive_range;
static double monitor_point;

static double constant_target_force;
static double constant_target_force_magnitude;

static void update_total_group_member_count(Py_ssize_t groupIndex, int count)//
{
//group index should run from 0
//default should set group_num = 0, and each group array size = 0

	int population_count=0;
	int i = 0, j=0;

	if (groupIndex < group_num && group_population_count !=NULL) {
		if(count == group_population_count[groupIndex]) return;
		else {
			group_population_count[groupIndex] = count;	
		}
	}
	else 
	{// when there is no group with this index, increase group num 
		group_num +=1;
		group_population_count = PyMem_Realloc(group_population_count, group_num * sizeof(int));
		//and allocate count for this group
		group_population_count[groupIndex] = count;	
	}

	//compute total population count, and corresponding counts for cd_inside group and between_groups
	for(i=0; i < group_num; i++) {
		population_count+= group_population_count[i];
	}		
	
	//re-allocate group_pedestrian number
	group_pedestrians = PyMem_Realloc(group_pedestrians, population_count * sizeof(Pedestrian));

}

static PyObject* get_population_size(PyObject* self)//
{
	int i;
	int population_count=0 ;
	for(i=0; i < group_num; i++) {
		population_count+= group_population_count[i];
	}
	return PyFloat_FromDouble(population_count);
}

static double double_from_attribute(PyObject * o, char * name)//
{
    PyObject * o2 = PyDict_GetItemString(o, name);
    double result = PyFloat_AsDouble(o2);
    return result;
}

static Vector vector_from_pyobject(PyObject * o)//
{
    Vector v;

    PyObject * x = PySequence_GetItem(o, 0);
    PyObject * y = PySequence_GetItem(o, 1);
    v.x = PyFloat_AsDouble(x);
    v.y = PyFloat_AsDouble(y);

    Py_DECREF(x);
    Py_DECREF(y);

    return v;
}

static Vector vector_from_attribute(PyObject * o, char * name)//
{
    PyObject * o2 = PyDict_GetItemString(o, name);
    Vector result = vector_from_pyobject(o2);
    return result;
}

static void pedestrian_from_pyobject(PyObject * o, Pedestrian * a)//
{

	a->pedestrian_id			= double_from_attribute(o,"pedestrian_id");
	a->group_id					= double_from_attribute(o,"group_id");
	a->radius                   = double_from_attribute(o, "radius");
  
	a->position         		= vector_from_attribute(o, "position");
	
    a->in_group_a_strength      = double_from_attribute(o, "in_group_a_strength");
    a->in_group_a_range			= double_from_attribute(o, "in_group_a_range");
    a->in_group_r_strength		= double_from_attribute(o, "in_group_r_strength");
    a->in_group_r_range			= double_from_attribute(o, "in_group_r_range");

    a->out_group_a_strength		= double_from_attribute(o,"out_group_a_strength");
    a->out_group_a_range		= double_from_attribute(o,"out_group_a_range");
	a->out_group_r_strength		= double_from_attribute(o,"out_group_r_strength");
	a->out_group_r_range		= double_from_attribute(o,"out_group_r_range");
	
	a->target_a_strength		= double_from_attribute(o,"target_a_strength");
	a->target_a_range			= double_from_attribute(o,"target_a_range");
	a->target 					= vector_from_attribute(o, "target");
	a->velocity					= 0.0;

	a->magnitude_target_force = 0.0;
	a->magnitude_wall_force = 0.0;
	a->velocity_x_direction = 0.0;
	a->magnitude_ingroup_force = 0.0;
	a->magnitude_outgroup_force = 0.0;

}

static PyObject * add_group_pedestrian(PyObject * self, PyObject * args)//
{
    PyObject * p_pedestrian;
	int group_id;
	int current_group_num, i=0;
	int population_remaining_groups = 0;
	int population_before_group = 0;
    PyArg_ParseTuple(args, "O:add_group_pedestrian", &p_pedestrian);
	group_id = double_from_attribute(p_pedestrian,"group_id");
	current_group_num = group_population_count[group_id];
		
	update_total_group_member_count(group_id,current_group_num+1);

	//should allocate index properly according to the size of each group, add to the last position of that group in the array of group_pedestrians
	i=0;
	while(i < group_num){
		if(i!=group_id) { //compute population of before and all after to add at correct position
			population_remaining_groups+= group_population_count[i];
			if (i< group_id){
				population_before_group+=group_population_count[i];
			}
		}
		else{
			population_remaining_groups +=0;
		}
		i++;
	}	
	for(i = population_remaining_groups + group_population_count[group_id] -1 ; i >= (group_population_count[group_id]+population_before_group); i--) {
			group_pedestrians[i] = group_pedestrians[i-1];
			
	}
	
	i = group_population_count[group_id] + population_before_group -1;
	pedestrian_from_pyobject(p_pedestrian, &group_pedestrians[i]);

    Py_RETURN_NONE;
}

static void rk_appropximate_level(int level_k, int population_count){//

	int i;
	if(level_k==1){ //compute at level 1
		for(i = 0; i < population_count; i++) {
			//reset acceleration at each  level 1 before computing it
			vector_imul(&group_pedestrians[i].acceleration_rk[0], 0.0);
			group_pedestrians[i].position_temp = group_pedestrians[i].position;

			//reset tracking target and wall force, in-group, out-group elements of RK4
			vector_imul(&group_pedestrians[i].magnitude_target_force_element[0], 0.0);
			vector_imul(&group_pedestrians[i].magnitude_wall_force_element[0], 0.0);
			vector_imul(&group_pedestrians[i].in_group_force_tracking_element[0],0.0);
			vector_imul(&group_pedestrians[i].out_group_force_tracking_element[0], 0.0);

			//reset the final target force and wall force, in-group, out-group force as well
			vector_imul(&group_pedestrians[i].target_force_tracking, 0.0);
			vector_imul(&group_pedestrians[i].wall_force_tracking,0.0);
			vector_imul(&group_pedestrians[i].in_group_force_tracking,0.0);
			vector_imul(&group_pedestrians[i].out_group_force_tracking,0.0);

		}

		for(i = 0; i < population_count; i++) {
			// compute desired force for pedestrian i by 0 index
			calculate_target_attraction(&group_pedestrians[i],0);
		}

		for(i = 0; i < population_count; i++) {
			// compute interaction attraction force for pedestrian i by 0 index
			calculate_pedestrian_repulsion_attraction(&group_pedestrians[i],i,0,population_count);
		}

		for(i = 0; i < population_count; i++) {
			// compute wall force for pedestrian i by 0 index
			calculate_wall_repulsion(&group_pedestrians[i],0);
		}

		//update position rk0
		for(i = 0; i < population_count; i++) {
			group_pedestrians[i].position_rk[0] = vector_mul(group_pedestrians[i].acceleration_rk[0], timestep);

		}
	}
	else if(level_k==2){ //compute at level 2
		for(i = 0; i < population_count; i++) {
			//reset acceleration at each  level k before computing it
			vector_imul(&group_pedestrians[i].acceleration_rk[1], 0.0);
			group_pedestrians[i].position_temp = vector_add(group_pedestrians[i].position, vector_mul(group_pedestrians[i].position_rk[0], 0.5));

			//reset tracking target force
			vector_imul(&group_pedestrians[i].magnitude_target_force_element[1], 0.0);
			vector_imul(&group_pedestrians[i].magnitude_wall_force_element[1], 0.0);
			vector_imul(&group_pedestrians[i].in_group_force_tracking_element[1],0.0);
			vector_imul(&group_pedestrians[i].out_group_force_tracking_element[1], 0.0);

		}

		for(i = 0; i < population_count; i++) {
			// compute desired force for pedestrian i by 0 index
			calculate_target_attraction(&group_pedestrians[i],1);
		}

		for(i = 0; i < population_count; i++) {
			// compute interaction force for pedestrian i at level 2 by 1 index
			calculate_pedestrian_repulsion_attraction(&group_pedestrians[i],i,1,population_count);
		}
		
		for(i = 0; i < population_count; i++) {
			// compute wall force for pedestrian i by 1 index
			calculate_wall_repulsion(&group_pedestrians[i],1);
		}

		for(i = 0; i < population_count; i++) {
			group_pedestrians[i].position_rk[1]= vector_mul(group_pedestrians[i].acceleration_rk[1], timestep);
		}
	}
	else if(level_k==3){ //compute at level 3
		for(i = 0; i < population_count; i++) {
			//reset acceleration at each  level k before computing it
			vector_imul(&group_pedestrians[i].acceleration_rk[2], 0.0);
			group_pedestrians[i].position_temp = vector_add(group_pedestrians[i].position, vector_mul(group_pedestrians[i].position_rk[1], 0.5));

			//reset tracking target force
			vector_imul(&group_pedestrians[i].magnitude_target_force_element[2], 0.0);
			vector_imul(&group_pedestrians[i].magnitude_wall_force_element[2], 0.0);
			vector_imul(&group_pedestrians[i].in_group_force_tracking_element[2],0.0);
			vector_imul(&group_pedestrians[i].out_group_force_tracking_element[2], 0.0);

		}

		for(i = 0; i < population_count; i++) {
			// compute desired force for pedestrian i by 0 index
			calculate_target_attraction(&group_pedestrians[i],2);
		}

		for(i = 0; i < population_count; i++) {
			// compute interaction force for pedestrian i at level 3 by 2 index
			calculate_pedestrian_repulsion_attraction(&group_pedestrians[i],i,2,population_count);
		}

		for(i = 0; i < population_count; i++) {
			// compute wall force for pedestrian i by 2 index
			calculate_wall_repulsion(&group_pedestrians[i],2);
		}

		for(i = 0; i < population_count; i++) {
			group_pedestrians[i].position_rk[2]  = vector_mul(group_pedestrians[i].acceleration_rk[2], timestep);
		}
	}
	else if(level_k==4){ //compute at level 4
		for(i = 0; i < population_count; i++) {
			//reset acceleration at each  level k before computing it
			vector_imul(&group_pedestrians[i].acceleration_rk[3], 0.0);
			group_pedestrians[i].position_temp = vector_add(group_pedestrians[i].position, group_pedestrians[i].position_rk[2]);

			//reset tracking target force
			vector_imul(&group_pedestrians[i].magnitude_target_force_element[3], 0.0);
			vector_imul(&group_pedestrians[i].magnitude_wall_force_element[3], 0.0);
			vector_imul(&group_pedestrians[i].in_group_force_tracking_element[3],0.0);
			vector_imul(&group_pedestrians[i].out_group_force_tracking_element[3], 0.0);

		}

		for(i = 0; i < population_count; i++) {
			// compute desired force for pedestrian i by 0 index
			calculate_target_attraction(&group_pedestrians[i],3);
		}

		for(i = 0; i < population_count; i++) {
			// compute interaction force for pedestrian i at level 4 by 3 index
			calculate_pedestrian_repulsion_attraction(&group_pedestrians[i],i,3,population_count);
		}
		
		for(i = 0; i < population_count; i++) {
			// compute wall force for pedestrian i by 3 index
			calculate_wall_repulsion(&group_pedestrians[i],3);
		}

		for(i = 0; i < population_count; i++) {
			group_pedestrians[i].position_rk[3] = vector_mul(group_pedestrians[i].acceleration_rk[3], timestep);
		}
	}

	return;	
}
	
static PyObject * update_pedestrians(PyObject * self, PyObject * args)//
{
	int i, population_count=0;	
	
	for(i=0; i < group_num; i++) {
		population_count+= group_population_count[i];
	}
	// update as RungeKutta, not as for each pedestrian
	// loop for all pedestrians regardless group or not, just check if they have the same group_id

	//compute RK level1
	rk_appropximate_level(1,population_count);
	//compute RK level2
	rk_appropximate_level(2,population_count);
	//compute RK level3
	rk_appropximate_level(3,population_count);
	//compute RK level4
	rk_appropximate_level(4,population_count);

	//update position for in-group pedestrians
	for(i = 0; i < population_count; i++) {
	   update_position(&group_pedestrians[i]);
	}

	//check escape
	//check_escapes();
	
	total_simulation_time+=timestep;


	Py_RETURN_NONE;
}

static void check_escapes()
{
	int i, j, population_count, group_id;
	int * escaped_count    = PyMem_Malloc(group_num * sizeof(int));

	population_count = 0;

	for (i=0; i < group_num; i++){
		population_count +=group_population_count[i];

	}

	for (i=0; i <group_num; i++ ){
		escaped_count[i] = 0;
	}


	for(i = 0, j = 0; i < population_count; i++) {
			if(!is_escaped(&group_pedestrians[i])) {
				group_pedestrians[j++] = group_pedestrians[i];

			} else {
				group_id = group_pedestrians[i].group_id;
				escaped_count[group_id] +=1;
			}
	}

	for (i=0; i <group_num; i++ ){
		if(escaped_count[i] != 0) {
			update_total_group_member_count(i,group_population_count[i]-escaped_count[i]);
		}
	}

	PyMem_Free(escaped_count);
}

static int is_escaped(Pedestrian * a)
{
	Vector currentposition = a->position;

	if (currentposition.x >= (monitor_point- a->radius)) return 1;
    return 0;
}


static void update_position(Pedestrian * a)//
{
	Vector delta_p, delta_p_temp;
	Vector delta_target_force, delta_target_force_temp;
	Vector delta_wall_force, delta_wall_force_temp;
	Vector delta_in_group_force, delta_in_group_force_temp;
	Vector delta_out_group_force, delta_out_group_force_temp;

	//update position
	delta_p = vector_add(a->position_rk[0],vector_mul(a->position_rk[1],2));
	delta_p_temp = vector_add(vector_mul(a->position_rk[2],2),a->position_rk[3]);
	vector_iadd(&delta_p,&delta_p_temp);
	vector_imul(&delta_p,1/6.0);
	a->position = vector_add(a->position,delta_p);
	a->velocity_direction = delta_p;

	a->velocity = vector_length(delta_p)/timestep;

	//update velocity on x-direction
	a->velocity_x_direction = (delta_p.x)/timestep;

	//update target_force_tracking
	delta_target_force = vector_add(a->magnitude_target_force_element[0],vector_mul(a->magnitude_target_force_element[1],2));
	delta_target_force_temp = vector_add(vector_mul(a->magnitude_target_force_element[2],2),a->magnitude_target_force_element[3]);
	vector_iadd(&delta_target_force,&delta_target_force_temp);
	vector_imul(&delta_target_force,1/6.0);
	a->magnitude_target_force = vector_length(delta_target_force);
	a->target_force_tracking = delta_target_force;

	//update wall_force_tracking
	delta_wall_force = vector_add(a->magnitude_wall_force_element[0],vector_mul(a->magnitude_wall_force_element[1],2));
	delta_wall_force_temp = vector_add(vector_mul(a->magnitude_wall_force_element[2],2),a->magnitude_wall_force_element[3]);
	vector_iadd(&delta_wall_force,&delta_wall_force_temp);
	vector_imul(&delta_wall_force,1/6.0);
	a->magnitude_wall_force = vector_length(delta_wall_force);
	a->wall_force_tracking = delta_wall_force;

	//update in-group force tracking
	delta_in_group_force = vector_add(a->in_group_force_tracking_element[0],vector_mul(a->in_group_force_tracking_element[1],2));
	delta_in_group_force_temp = vector_add(vector_mul(a->in_group_force_tracking_element[2],2),a->in_group_force_tracking_element[3]);
	vector_iadd(&delta_in_group_force,&delta_in_group_force_temp);
	vector_imul(&delta_in_group_force,1/6.0);
	a->magnitude_ingroup_force = vector_length(delta_in_group_force);
	a->in_group_force_tracking = delta_in_group_force;

	//update out-group force tracking
	delta_out_group_force = vector_add(a->out_group_force_tracking_element[0],vector_mul(a->out_group_force_tracking_element[1],2));
	delta_out_group_force_temp = vector_add(vector_mul(a->out_group_force_tracking_element[2],2),a->out_group_force_tracking_element[3]);
	vector_iadd(&delta_out_group_force,&delta_out_group_force_temp);
	vector_imul(&delta_out_group_force,1/6.0);
	a->magnitude_outgroup_force = vector_length(delta_out_group_force);
	a->out_group_force_tracking = delta_out_group_force;

}

static PyObject* target_changed(PyObject * self, PyObject * args){

	int ped_index;
	Vector new_target;
    PyObject * additional_data;

    PyArg_ParseTuple(args, "O:target_changed", &additional_data);

	ped_index = (int)double_from_attribute(additional_data,"ped_index");
	new_target = vector_from_attribute(additional_data, "target");

	group_pedestrians[ped_index].target.x = new_target.x;
	group_pedestrians[ped_index].target.y = new_target.y;

	return Py_BuildValue("dd",
			new_target.x, new_target.y);
}

static void calculate_target_attraction(Pedestrian *a, int level_rk)
{
	Vector target_attraction     = vector_sub(a->position_temp, a->target);
	double distance   = fabs(vector_length(target_attraction) - a->radius);
	double attraction_strength = -1 * (a->target_a_strength * exp((-distance)/a->target_a_range));

	vector_unitise(&target_attraction);

	if(constant_target_force == 1) {
		vector_imul(&target_attraction,(-1 * constant_target_force_magnitude));
	} else {
		vector_imul(&target_attraction,attraction_strength);
	}

	vector_iadd(&a->acceleration_rk[level_rk], &target_attraction);

	//reset tracking target force
	vector_iadd(&a->magnitude_target_force_element[level_rk], &target_attraction);
}

static void  calculate_pedestrian_repulsion_attraction(Pedestrian *a,int index, int level_rk, int population_count)//
{
	int j;
	Vector interaction;
	double repulsion_strength, attraction_strength;
	int group_id; 
	//compute attraction force for group pedestrian
	for(j = 0; j < population_count; j++) {
		if(index == j) continue;
		
		group_id = group_pedestrians[j].group_id;
		repulsion_strength = 0;
		attraction_strength = 0;
		interaction.x = 0.0;
		interaction.y = 0.0; 
		
		if(a->group_id == group_id) {		
			//we compute the repulsion force between this two pedestrians in the same group
			repulsion_strength = calculate_magnitude_repulsion_vector(a,group_pedestrians[j], 1);
		    //we compute the attraction force between this two pedestrians
			attraction_strength = calculate_magnitude_attraction_vector(a,group_pedestrians[j], 1);

			
		} else {
			//we compute the repulsion force between this two pedestrians in different groups
			repulsion_strength = calculate_magnitude_repulsion_vector(a,group_pedestrians[j], 2);
		    //we compute the attraction force between this two pedestrians in different groups
			attraction_strength = calculate_magnitude_attraction_vector(a,group_pedestrians[j], 2);
			
		}
		repulsion_strength -=attraction_strength;
		interaction = vector_sub(a->position_temp, group_pedestrians[j].position_temp);
		vector_unitise(&interaction);
		vector_imul(&interaction,repulsion_strength);
		vector_iadd(&a->acceleration_rk[level_rk], &interaction);

		//set in-group or out-group force tracking
		if(a->group_id == group_id) {
			vector_iadd(&a->in_group_force_tracking_element[level_rk],&interaction);
		} else {
			vector_iadd(&a->out_group_force_tracking_element[level_rk], &interaction);
		}

	}
}

//this method is to calculate the attraction force created by Pedestrian b on Pedestrian * a
static double calculate_magnitude_repulsion_vector(Pedestrian *a, Pedestrian b, int group_type)//
{
	double radius_sum = a->radius + b.radius;
	Vector from_b     = vector_sub(a->position_temp, b.position_temp);
	double distance   = fabs(vector_length(from_b) - radius_sum);

	double repulsion_strength = 0;
	if (group_type==1){
		repulsion_strength = a->in_group_r_strength * exp((-distance)/a->in_group_r_range);
	} else {
		repulsion_strength = a->out_group_r_strength * exp((-distance)/a->out_group_r_range);
	}
	return repulsion_strength;
}

//this method is to calculate the attraction force created by Pedestrian b on Pedestrian * a
static double calculate_magnitude_attraction_vector(Pedestrian *a, Pedestrian b, int group_type)//
{
	double radius_sum = a->radius + b.radius;
	Vector from_b     = vector_sub(a->position_temp, b.position_temp);
	double distance   = fabs(vector_length(from_b) - radius_sum);

	double attraction_strength = 0.0;
	if (group_type==1){ 
		attraction_strength = a->in_group_a_strength * exp((-distance)/a->in_group_a_range);
	} else {
		attraction_strength = a->out_group_a_strength * exp((-distance)/a->out_group_a_range);
	}
	return attraction_strength;
}

//this method is to retrieve information of group member a
static PyObject * group_pedestrian_a_property(PyObject * self, PyObject * args)//
{
    int i;
	char * property;
    Vector desired_direction;

    PyArg_ParseTuple(args, "is:group_pedestrian_a_property", &i, &property);

	if(strcmp(property, "position") == 0) {
		return Py_BuildValue("dd",
				group_pedestrians[i].position.x, group_pedestrians[i].position.y);
	}else if(strcmp(property, "radius") == 0) {
		return PyFloat_FromDouble(group_pedestrians[i].radius);
	}else if (strcmp(property, "groupid") == 0){
		return PyFloat_FromDouble(group_pedestrians[i].group_id);
	}else if (strcmp(property, "ped_id") == 0){
		return PyFloat_FromDouble(group_pedestrians[i].pedestrian_id);

	}else if  (strcmp(property, "velocity") == 0){
		return PyFloat_FromDouble(group_pedestrians[i].velocity);

	}else if  (strcmp(property, "target_force") == 0){
		return PyFloat_FromDouble(group_pedestrians[i].magnitude_target_force);
	}else if  (strcmp(property, "wall_force") == 0){
		return PyFloat_FromDouble(group_pedestrians[i].magnitude_wall_force);
	}else if  (strcmp(property, "ingroup_force") == 0){
		return PyFloat_FromDouble(group_pedestrians[i].magnitude_ingroup_force);
	} else if (strcmp(property, "outgroup_force") == 0){
	    return PyFloat_FromDouble(group_pedestrians[i].magnitude_outgroup_force);

	} else if (strcmp(property, "velocity_x") == 0){
		return PyFloat_FromDouble(group_pedestrians[i].velocity_x_direction);

	} else if (strcmp(property, "velocity_direction") == 0){
			return Py_BuildValue("dd",
							group_pedestrians[i].velocity_direction.x, group_pedestrians[i].velocity_direction.y);
	} else if (strcmp(property, "desired_direction") == 0){
			desired_direction     = vector_sub(group_pedestrians[i].target, group_pedestrians[i].position);
			vector_unitise(&desired_direction);
			return Py_BuildValue("dd",
					desired_direction.x, desired_direction.y);

	} else if (strcmp(property, "target") == 0){
		return Py_BuildValue("dd",group_pedestrians[i].target.x, group_pedestrians[i].target.y);

	} else if(strcmp(property,"target_vector") == 0){
		return Py_BuildValue("dd",group_pedestrians[i].target_force_tracking.x, group_pedestrians[i].target_force_tracking.y);
	} else if(strcmp(property,"wall_vector") == 0){
		return Py_BuildValue("dd",group_pedestrians[i].wall_force_tracking.x, group_pedestrians[i].wall_force_tracking.y);
	} else if(strcmp(property,"ingroup_vector") == 0){
		return Py_BuildValue("dd",group_pedestrians[i].in_group_force_tracking.x, group_pedestrians[i].in_group_force_tracking.y);
	} else if(strcmp(property,"outgroup_vector") == 0){
		return Py_BuildValue("dd",group_pedestrians[i].out_group_force_tracking.x, group_pedestrians[i].out_group_force_tracking.y);
	}


	PyErr_SetString(PyExc_AttributeError, property);
	return NULL;
}

static PyObject* check_escaped_by_id(PyObject * self, PyObject * args) {
	int i, ped_id, population_count;
    PyArg_ParseTuple(args, "is:check_escaped_by_id", &ped_id);

    population_count =0;
    for(i=0; i < group_num; i++) {
	 		population_count+= group_population_count[i];
	}

    for(i=0; i < population_count;i++){
   		  if (group_pedestrians[i].pedestrian_id == ped_id) {
   			  return  PyFloat_FromDouble(1.0);
   		  }
    }
    return PyFloat_FromDouble(0);

}

static PyObject* group_pedestrian_id_property(PyObject * self, PyObject * args) {

	  int i, ped_id, population_count;
	  char * property;
	  PyArg_ParseTuple(args, "is:group_pedestrian_id_property", &ped_id, &property);

	  population_count =0;

	  for(i=0; i < group_num; i++) {
	  		population_count+= group_population_count[i];
	  }

	  for(i=0; i < population_count;i++){
		  if (group_pedestrians[i].pedestrian_id == ped_id) {

			  if(strcmp(property, "position") == 0) {
			  		return Py_BuildValue("dd",
			  				group_pedestrians[i].position.x, group_pedestrians[i].position.y);
			  }else if(strcmp(property, "radius") == 0) {
				  	return PyFloat_FromDouble(group_pedestrians[i].radius);
			  }else if (strcmp(property, "groupid") == 0){
				  	return PyFloat_FromDouble(group_pedestrians[i].group_id);
			  }else if (strcmp(property, "ped_id") == 0){
			  		return PyFloat_FromDouble(group_pedestrians[i].pedestrian_id);

			  }else if  (strcmp(property, "velocity") == 0){
				  	return PyFloat_FromDouble(group_pedestrians[i].velocity);

			  }else if  (strcmp(property, "target_force") == 0){
			  		return PyFloat_FromDouble(group_pedestrians[i].magnitude_target_force);
			  }else if  (strcmp(property, "wall_force") == 0){
			  		return PyFloat_FromDouble(group_pedestrians[i].magnitude_wall_force);
			  } else if  (strcmp(property, "ingroup_force") == 0){
			  		return PyFloat_FromDouble(group_pedestrians[i].magnitude_ingroup_force);
			  } else if (strcmp(property, "outgroup_force") == 0){
				    return PyFloat_FromDouble(group_pedestrians[i].magnitude_outgroup_force);

			  } else if (strcmp(property, "velocity_x") == 0){
			  		return PyFloat_FromDouble(group_pedestrians[i].velocity_x_direction);
			  } else if (strcmp(property, "target") == 0){
				  return Py_BuildValue("dd",group_pedestrians[i].target.x, group_pedestrians[i].target.y);

			  } else if(strcmp(property,"target_vector") == 0){
			  		return Py_BuildValue("dd",group_pedestrians[i].target_force_tracking.x, group_pedestrians[i].target_force_tracking.y);
			  } else if(strcmp(property,"wall_vector") == 0){
			  		return Py_BuildValue("dd",group_pedestrians[i].wall_force_tracking.x, group_pedestrians[i].wall_force_tracking.y);
			  } else if(strcmp(property,"ingroup_vector") == 0){
			  		return Py_BuildValue("dd",group_pedestrians[i].in_group_force_tracking.x, group_pedestrians[i].in_group_force_tracking.y);
			  } else if(strcmp(property,"outgroup_vector") == 0){
			  		return Py_BuildValue("dd",group_pedestrians[i].out_group_force_tracking.x, group_pedestrians[i].out_group_force_tracking.y);
			  }
		  }
	  }

	  return PyFloat_FromDouble(-999.0);
	  PyErr_SetString(PyExc_AttributeError, property);
	  return NULL;
}


static void calculate_wall_repulsion(Pedestrian * a,int level_rk){
	 int i;
	 Vector * repulsion_points  = PyMem_Malloc(w_count * sizeof(Vector));
	 int rep_p_c = 0;
	 Vector repulsion;

	 rep_p_c = find_wall_repulsion_points(a, repulsion_points);

	 for(i = 0; i < rep_p_c; i++) {
	     repulsion = calculate_wall_repulsion_point(a, repulsion_points[i]);
	     vector_iadd(&a->acceleration_rk[level_rk], &repulsion);

	     vector_iadd(&a->magnitude_wall_force_element[level_rk], &repulsion);
	 }

	 PyMem_Free(repulsion_points);
}

static Vector calculate_wall_repulsion_point(Pedestrian * a, Vector repulsion_point)
{
	Vector from_wall     = vector_sub(a->position_temp, repulsion_point);
	double distance   = fabs(vector_length(from_wall) - a->radius);

	double repulsion_strength = wall_repulsive_strength * exp((-distance)/wall_repulsive_range);

	vector_unitise(&from_wall);
	vector_imul(&from_wall,repulsion_strength);

	return from_wall;
}

static int find_wall_repulsion_points(Pedestrian * a, Vector repulsion_points[])
{
	int i,j;
	double projection_length;
	Vector * used_endpoints    = PyMem_Malloc(2*w_count * sizeof(Vector));
	Vector * possible_endpoints = PyMem_Malloc(w_count * sizeof(Vector));
	int rep_p_c = 0, use_e_c = 0, pos_e_c = 0;

	for(i = 0; i < w_count; i++) {
	    Wall w = walls[i];
	    projection_length = vector_projection_length(w.start, w.end, a->position_temp);
	    if(projection_length < 0)  {
	         possible_endpoints[pos_e_c++] = w.start;
	    } else if(projection_length > w.length) {
	        possible_endpoints[pos_e_c++] = w.end;
	    } else {
	            // We have the length, L, of how far along AB the projection point is.
	            // To turn this into a point, we multiply AB with L/|AB| and add
	            // this vector to the starting point A.
				// P = A + AB*L/|AB|
	       repulsion_points[rep_p_c++] = vector_add(w.start,
	                vector_mul(vector_sub(w.end, w.start),
	                projection_length/w.length));
	       used_endpoints[use_e_c++] = w.start;
	       used_endpoints[use_e_c++] = w.end;
	     }
	}

	for(i = 0; i < pos_e_c; i++) {
	   int use_e = 1;
	   for(j = 0; j < use_e_c; j++) {
		   if(vector_equals(possible_endpoints[i], used_endpoints[j])) {
	             use_e = 0;
	       }
	   }
	   if(use_e) {
		// Keep track of whether the endpoint is free-floating, i.e. if
		// it is shared with another wall as near bottle neck
		   int free_e = 1;
			for(j = 0; j < pos_e_c; j++) {
				if(i != j && vector_equals(possible_endpoints[i],
								possible_endpoints[j])) {
					free_e = 0;
				}
			}
				// Endpoints that are free-floating (i.e. sides of doorways) are
				// only considered for repulsion if they are closer to the pedestrian
				// than the pedestrian's radius. This allows pedestrians to pass more
				// freely through doorways.
				// *** a minimum gap between two walls ****
			if(!free_e ||
				vector_length(vector_sub(a->position_temp,
						possible_endpoints[i])) < a->radius) {
				repulsion_points[rep_p_c++] = possible_endpoints[i];
				used_endpoints[use_e_c++] = possible_endpoints[i];
			}
	   }
	}

	PyMem_Free(used_endpoints);
	PyMem_Free(possible_endpoints);

	return rep_p_c;
}

static PyObject * set_parameters(PyObject * self, PyObject * args)//
{
	PyObject * o, * p_walls;
	int i;
	PyArg_ParseTuple(args, "O:set_parameters", &o);

	timestep    = double_from_attribute(o, "timestep");

	//set total simulation time
	total_simulation_time = 0;

	//set group_num
	group_num	= double_from_attribute(o, "group");
	
	//set constant target force
	constant_target_force = double_from_attribute(o, "constant_target");
	constant_target_force_magnitude = double_from_attribute(o, "constant_target_magnitude");

	//set group number for each group
	group_population_count = PyMem_Malloc(group_num * sizeof(int));
	
	for(i=0; i < group_num; i++)
		group_population_count[i] = 0;
	
	group_pedestrians=NULL;
	group_pedestrians = PyMem_Realloc(group_pedestrians, 0 * sizeof(Pedestrian));

	//set monitor point
	monitor_point  = double_from_attribute(o, "monitor_point");

	//set walls
	wall_repulsive_strength          = double_from_attribute(o, "w_R");
	wall_repulsive_range			 = double_from_attribute(o, "w_r");

	p_walls     = PyDict_GetItemString(o, "walls");
	w_count = PyList_Size(p_walls);
	walls    = PyMem_Realloc(walls, w_count * sizeof(Wall));
	init_walls(p_walls, walls, w_count);

	Py_RETURN_NONE;
}

static PyObject * set_start_simulation_time(PyObject * self, PyObject * args)//
{
	  double start;
	  PyArg_ParseTuple(args, "d:set_start_simulation_time", &start);
	  total_simulation_time = start;

	  Py_RETURN_NONE;
}

static Wall wall_from_pyobject(PyObject *o)
{
    Wall w;
    w.start.x = PyFloat_AsDouble(PyTuple_GetItem(o, 0));
    w.start.y = PyFloat_AsDouble(PyTuple_GetItem(o, 1));
    w.end.x   = PyFloat_AsDouble(PyTuple_GetItem(o, 2));
    w.end.y   = PyFloat_AsDouble(PyTuple_GetItem(o, 3));
    w.length  = vector_length(vector_sub(w.end, w.start));

    return w;
}

static void init_walls(PyObject * p_walls, Wall * walls_p, Py_ssize_t w_count)
{
    int i;
    for(i = 0; i < w_count; i++) {
        PyObject * p_w   = PyList_GetItem(p_walls, i);
        Wall w = wall_from_pyobject(p_w);
        walls_p[i] = w;
    }
}

static PyObject * reset_model(PyObject* self)//
{
	int i;
	for(i=0; i < group_num; i++)
		group_population_count[i] = 0;

	group_pedestrians = PyMem_Realloc(group_pedestrians, 0 * sizeof(Pedestrian));

	//set total simulation time
	total_simulation_time = 0;

	Py_RETURN_NONE;
}

static PyMethodDef ForceModelMethods[] = {
    {"add_group_pedestrian", add_group_pedestrian, METH_VARARGS, //
        "Add an group member to the list"},
	{"set_parameters",set_parameters,METH_VARARGS,//
		"Set simulation parameters"},
	{"group_pedestrian_a_property", group_pedestrian_a_property, METH_VARARGS, ////
        "Get an property for group members"},	
	{"get_population_size",(PyCFunction)get_population_size,METH_NOARGS,////
		"Get total population number"},
	{"update_pedestrians",update_pedestrians,METH_VARARGS,//
		"Calculate the acceleration of an pedestrian"},
	{"reset_model",(PyCFunction)reset_model,METH_NOARGS,
		"Reset model for parameters and pedestrians"},
	{"group_pedestrian_id_property", group_pedestrian_id_property, METH_VARARGS, ////
	    "Get an property for group members by id"},
	{"check_escaped_by_id",check_escaped_by_id,METH_VARARGS,
			"Check escaped or not by id"},
	{"set_start_simulation_time", set_start_simulation_time, METH_VARARGS,
		"Set initial simulation time"},
	{"target_changed", target_changed, METH_VARARGS,
		"Change target in turning corridor"},

	{NULL, NULL, 0, NULL}
};

static struct PyModuleDef forceCalculationmodule = {
		PyModuleDef_HEAD_INIT,
		"socialforce",
		NULL,
		-1,
		ForceModelMethods
	};

PyMODINIT_FUNC PyInit_socialforce(void)
{
	PyObject * m;
	m = PyModule_Create(&forceCalculationmodule);	
    return m;
}
