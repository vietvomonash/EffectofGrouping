#include <Python.h>
#include <math.h>
#include "vector.h"

#define PI 3.14159265

typedef struct {

    double pedestrian_id; //=pedestrian Id for tracking purpose
	int group_id;
    double radius;
	
	Vector position;
	
	double velocity;
	double velocity_x_direction;
	Vector velocity_direction;

    double in_group_a_strength; //=A
    double in_group_a_range; //=a
    double in_group_r_strength; //=R
    double in_group_r_range;//=r

    double out_group_a_strength; //A
    double out_group_a_range;//a
	double out_group_r_strength;//R
	double out_group_r_range;//r

	double target_a_strength; //t_A
	double target_a_range; //t_a
	Vector target;
	
	Vector acceleration_rk[4]; //rk for each order
	Vector position_rk[4];//rk for each order

	Vector position_temp; //this is temporary position used to calculate acceleration at each RK order
	
	double magnitude_target_force;
	Vector magnitude_target_force_element[4];
	Vector target_force_tracking;

	double magnitude_wall_force;
	Vector magnitude_wall_force_element[4];
	Vector wall_force_tracking;

	double magnitude_ingroup_force;
	Vector in_group_force_tracking;
	Vector in_group_force_tracking_element[4];

	double magnitude_outgroup_force;
	Vector out_group_force_tracking;
	Vector out_group_force_tracking_element[4];

} Pedestrian;

typedef struct {
    Vector start;
    Vector end;
    double length;
} Wall;

/**** initial methods****/
static PyObject * add_group_pedestrian(PyObject * self, PyObject * args);//
static PyObject * set_parameters(PyObject * self, PyObject * args);//
static PyObject * update_pedestrians(PyObject * self, PyObject * args);//
static void update_position(Pedestrian * a);//
static void update_total_group_member_count(Py_ssize_t groupIndex, int count);//
static void rk_appropximate_level(int level_k, int population_count);//
static void check_escapes();
static int is_escaped(Pedestrian * a);
static PyObject * set_start_simulation_time(PyObject * self, PyObject * args);
static PyObject* target_changed(PyObject * self, PyObject * args);


static void pedestrian_from_pyobject(PyObject * o, Pedestrian * a);//
static double double_from_attribute(PyObject * o, char * name);//
static Vector vector_from_attribute(PyObject * o, char * name);//
static Vector vector_from_pyobject(PyObject * o);//

static Wall wall_from_pyobject(PyObject *o);
static void init_walls(PyObject * p_walls, Wall * walls_p, Py_ssize_t w_count);
static int find_wall_repulsion_points(Pedestrian * a, Vector repulsion_points[]);
static Vector calculate_wall_repulsion_point(Pedestrian * a, Vector repulsion_point);

/**** update model methods ****/
static void calculate_target_attraction(Pedestrian *a, int level_rk);
static void calculate_pedestrian_repulsion_attraction(Pedestrian *a,int index, int level_rk, int population_count);//
static void calculate_wall_repulsion(Pedestrian * a, int level_rk);
static double calculate_magnitude_attraction_vector(Pedestrian *a, Pedestrian b,int group_type);//
static double calculate_magnitude_repulsion_vector(Pedestrian *a, Pedestrian b,int group_type);

/*** get methods ****/
static PyObject* group_pedestrian_a_property(PyObject * self, PyObject * args);//
static PyObject* group_pedestrian_id_property(PyObject * self, PyObject * args);//

static PyObject* get_population_size(PyObject* self);//
static PyObject* check_escaped_by_id(PyObject * self, PyObject * args);//
/*** reset model ***/
static PyObject * reset_model(PyObject* self);//


