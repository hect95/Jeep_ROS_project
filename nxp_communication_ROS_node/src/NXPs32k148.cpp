#include "NXPS32k148Lib.h"

#include <unistd.h>
#define BYTES_PER_FLOAT 4

NXPs32k148::NXPs32k148(I2C_Device* NXP,bool thread){
  NXP_ = NXP;
  if(thread)
    sending_ = std::thread(&NXPs32k148::send_acceleration_breaking_direction, this);
}

NXPs32k148::~NXPs32k148(){
  delete NXP_;
  kill_i2c_thread = 1;
  sending_.join();
  std::cout << "Count cycles = " << count_cycles << std::endl;
}

/*Sets references points for acceleration, direction and breaking */
void NXPs32k148::set_reference_points(float acc, float dir, float brk){
  mtx.lock();
  acceleration_.flotante = acc;
  direction_.flotante    = dir;
  break_.flotante        = brk;
  mtx.unlock();
  std::cout << "HEX representation of :" << acceleration_.flotante << " is :" << std::hex << (int)acceleration_.hex << std::endl;
}


std::uint8_t NXPs32k148::get_n_byte(std::uint32_t un, int pos){
  int ret;
  if(pos < 4){ret = (std::uint8_t)((un >> pos*bits_in_byte) & 0x000000FF);}
  else {ret = 0;}
	return ret;
}

/*Sends references through I2C on time*/
void NXPs32k148::send_acceleration_breaking_direction_one_time(){
    std::vector<std::uint8_t> bytes_a_mandar;
    
    for(unsigned int data = 0; data < data_to_send.size(); data++){
      for(int i = 0; i < BYTES_PER_FLOAT; i++){
        bytes_a_mandar.push_back(get_n_byte(data_to_send[data]->hex,i));
        std::cout << "bytes to be send "<< data*4+i+1 << " = " << std::hex << (int)bytes_a_mandar.at(data*4+i) << std::endl;

      }
    }
    int check = NXP_->write_I2CDevice_block_of_u8(bytes_a_mandar);
    if(check == -1){
      std::cout << "Error bus i2c: errno -> " << error << std::endl;
    }
    else {
      std::cout << check << " bytes were written correctly through I2C\n";
    }
    bytes_a_mandar.clear();


}

/*Wait function*/
void wait(std::chrono::microseconds period, Clock::time_point& beginning,Clock::time_point& end){
  beginning = Clock::now();
  while(std::chrono::duration_cast<std::chrono::microseconds>(end - beginning).count()  < std::chrono::duration_cast<std::chrono::microseconds>(period).count()){
    usleep(1000);
    end = Clock::now();
  }
}

/*Send references constantly if required*/
void NXPs32k148::send_acceleration_breaking_direction(){
    std::vector<std::uint8_t> bytes_a_mandar;
    while(1){
		count_cycles++;

  //Reset clock after 10000us duration
    wait(step, time_begin, time_count);
    if(kill_i2c_thread){break;}
  //Sending I2C Data
    for(unsigned int data = 0; data < data_to_send.size(); data++){
      for(int i = 0; i < BYTES_PER_FLOAT; i++){
        mtx.lock();
        bytes_a_mandar.push_back(get_n_byte(data_to_send[data]->hex,i));
        mtx.unlock();
      }
    }
    int check = NXP_->write_I2CDevice_block_of_u8(bytes_a_mandar);
    if(check == -1){
      std::cout << "Error en el bus i2c: errno -> " << error << std::endl;
    }
    else {
      std::cout << "Se escribieron correctamente " << check << " bytes a traves de i2c\n";
    }
    bytes_a_mandar.clear();

    }
}
