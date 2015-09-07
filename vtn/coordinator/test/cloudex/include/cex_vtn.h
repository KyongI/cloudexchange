//cex_vtn.h
//
//TODO : 아래의 class 를 분리해야 한다. 
//       unc::driver::controller class
//       unc::vtndrvcache::ConfigNode class 
//REP : coordinator/modules/odcdriver/include/odc_vtn.hh
#ifndef _CEX_VTN_HH_
#define _CEX_VTN_HH_

#include <vector>
#include <string>
#include <sstream>
#include <unc_base/h> //define UncRespCode
#include "cex_common.h"

class VtnCommand {
 public:
  explicit VtnCommand(ConfFileValues_t conf_values);
  ~VtnCommand();

  /**
   * @brief                          - Frames VTN Create command and uses rest
   *                                   client interface to send it to VTN Manager
   * @param[in] key_vtn_t            - key structure of VTN
   * @param[in] val_vtn_t            - value structure of VTN
   * @param[in] ctr                  - Controller pointer
   * @return                         - returns UNC_RC_SUCCESS on
   *                                   creation of vtn/ returns
   *                                   UNC_DRV_RC_ERR_GENERIC on failure
   */
  UncRespCode create_cmd(key_vtn_t& key, val_vtn_t& val,
                         unc::driver::controller *ctr);

  /**
   * @brief                          - Frames VTN update command and uses rest client
   *                                   interface to send it to VTN Manager
   * @param[in] key_vtn_t            - key structure of VTN
   * @param[in] val_vtn_t            - Old value structure of VTN
   * @param[in] val_vtn_t            - New value structure of VTN
   * @param[in] ctr                  - Controller pointer
   * @return                         - returns UNC_RC_SUCCESS on
   *                                   updation of vtn /returns
   *                                   UNC_DRV_RC_ERR_GENERIC on failure
   */
  UncRespCode update_cmd(key_vtn_t& key, val_vtn_t& val_old,
                         val_vtn_t& val_new,
                         unc::driver::controller *ctr);

  /**
   * @brief                          - Frames VTN delete command and uses rest
   *                                   client interface to send it to VTN Manager
   * @param[in] key_vtn_t            - key structure of VTN
   * @param[in] val_vtn_t            - value structure of VTN
   * @param[in] ctr                  - Controller pointer
   * @return                         - returns UNC_RC_SUCCESS on
   *                                   deletion/returns UNC_DRV_RC_ERR_GENERIC
   *                                   on failure
   */
  UncRespCode delete_cmd(key_vtn_t& key, val_vtn_t& val,
                         unc::driver::controller *ctr);
  /**
   * @brief                          - get all the vtns from the VTN Manager
   * @param[in] ctr                  - Controller pointer
   * @param[out] cfg_node_vector      - cfg_node_vector - out parameter contains
   *                                   list of vtns present in controller
   * @return UncRespCode         - returns UNC_RC_SUCCESS on
   *                                   success of read all operation/returns
   *                                   UNC_DRV_RC_ERR_GENERIC on failure
   */
  UncRespCode get_vtn_list(
      unc::driver::controller* ctr,
      std::vector<unc::vtndrvcache::ConfigNode *> &cfg_node_vector);

};
#endif
