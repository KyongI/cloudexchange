//cex_vbrif.h
//

#ifndef _CEX_VLINK_HH
#define _CEX_VLINK_HH

#include <unc/upll_ipc_enum.h>
#include <unc/pfcdriver_ipc_enum.h>
#include <string>
#include <vector>
#include <sstream>
#include <unc_base/h> //define UncRespCode
#include "cex_common.h"
#include "cex_vtn.h"

class OdcVlinkCommand: {
 public:
  explicit OdcVlinkCommand(ConfFileValues_t conf_values);
  ~OdcVlinkCommand();

  /**
   * @brief      - Creates VLink
   * @param[in]  - key structure of VLink
   * @param[in]  - value structure of VLink
   * @param[in]  - Controller connection information
   * @retval     - returns DRVAPI_RESPONSE SUCCESS on creation of VLink successfully
   *               /returns UNC_DRV_RC_ERR_GENERIC on failure
   */
  UncRespCode create_cmd(key_vlink_t& key,
                         pfcdrv_val_vlink_t& val,
                         unc::driver::controller *conn);

  /**
   * @brief                      - Updates VLink
   * @param[in] key              - key structure of VLink
   * @param[in] val              - Old value structure of VLink
   * @param[in] val              - New value structure of VLink
   * @param[in] conn             - Controller connection information
   * @retval UncRespCode         - returns UNC_RC_SUCCESS on updation of VLink
   *                               successfully/returns UNC_DRV_RC_ERR_GENERIC on failure
   */
  UncRespCode update_cmd(key_vlink_t& key,
                         pfcdrv_val_vlink_t& val_old,
                         pfcdrv_val_vlink_t& val_new,
                         unc::driver::controller *conn);

  /**
   * @brief                    - Deletes VLink
   * @param[in] key            - key structure of VLink
   * @param[in] val            - value structure of VLink
   * @param[in] conn           - Controller connection information
   * @return UncRespCode       - returns UNC_RC_SUCCESS on deletion of
   *                             VLink successfully /returns
   *                             UNC_DRV_RC_ERR_GENERIC on failure
   */
  UncRespCode delete_cmd(key_vlink_t& key,
                         pfcdrv_val_vlink_t& val,
                         unc::driver::controller *conn);

  /**
   * @brief                           - get all the vlink child
   * @param[in] vtn_name              - vtn name
   * @param[in] vlk_name              - vlink name
   * @param[in] ctr                   - controller pointer
   * @param[out] cfgnode_vector       - config node vector
   * @return UncRespCode              - returns UNC_RC_SUCCESS on successfully retieving a vlink
   *                                    child /returns UNC_DRV_RC_ERR_GENERIC on failure
   */
  UncRespCode get_vlink_list(
      std::string vtn_name,
      std::string vlk_name,
      unc::driver::controller* ctr,
      std::vector< unc::vtndrvcache::ConfigNode *> &cfgnode_vector);

};
#endif
